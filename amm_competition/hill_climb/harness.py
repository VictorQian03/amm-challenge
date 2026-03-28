"""Append-only hill-climb harness for agent-driven strategy iteration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import time
from typing import Any, Protocol

from amm_competition.competition.eval import compute_scorecard
from amm_competition.competition.protected_surface import (
    ProtectedSurfaceChecker,
    ProtectedSurfaceError,
)
from amm_competition.evm.adapter import EVMStrategyAdapter
from amm_competition.evm.baseline import load_vanilla_strategy
from amm_competition.evm.compiler import SolidityCompiler
from amm_competition.evm.validator import SolidityValidator
from amm_competition.hill_climb.stages import (
    HILL_CLIMB_STAGES,
    build_stage_runner,
    resolve_hill_climb_stage,
)

ARTIFACT_VERSION = "hill_climb.v2"
RUN_MANIFEST_VERSION = "hill_climb.run.v3"
RUN_STATE_VERSION = "hill_climb.state.v1"
SNAPSHOT_LAYOUT_VERSION = "flat_snapshots.v1"
INCUMBENT_EPSILON = 1e-9
NEXT_EVAL_INDEX_FILENAME = ".next_eval_index"
LEGACY_NEXT_EVAL_ID_FILENAME = ".next_eval_id"
DEFAULT_ACTIVE_STRATEGY_PATH = Path("contracts/src/Strategy.sol")
DEFAULT_STOP_RULES = {
    "refine_after_non_improving_iterations": 3,
    "pivot_after_non_improving_iterations": 5,
    "stop_after_non_improving_iterations": 8,
}
RESULTS_HEADER = (
    "eval_id\tstage\tstatus\tmean_edge\tincumbent_mean_edge\tdelta_vs_incumbent\t"
    "strategy_name\tlabel\tdescription\tsnapshot_path\n"
)


class HillClimbHarnessError(RuntimeError):
    """Raised when hill-climb setup or execution is invalid."""


@dataclass(frozen=True)
class StageStatus:
    """Compact incumbent and recent-result view for one stage."""

    run_id: str
    stage: str
    incumbent: dict[str, Any] | None
    latest: dict[str, Any] | None


@dataclass(frozen=True)
class LoopGuidance:
    """Derived operator guidance from the retained loop state."""

    non_improving_streak: int
    action: str
    message: str


@dataclass(frozen=True)
class RunStateStatus:
    """Validated persisted loop state plus derived operator guidance."""

    run_id: str
    baseline_eval_id: str | None
    current_target_stage: str
    incumbent_eval_ids: dict[str, str]
    last_completed_iteration: int
    next_hypothesis: str | None
    run_mode: str
    stop_rules: dict[str, int]
    updated_at: str
    guidance: LoopGuidance


@dataclass(frozen=True)
class SelectionDecision:
    """Explain whether a candidate cleared the incumbent replacement margin."""

    status: str
    delta: float | None
    promotion_margin: float | None
    rationale: str


class StrategyLoader(Protocol):
    """Load a strategy adapter from Solidity source text."""

    def __call__(self, source_text: str) -> EVMStrategyAdapter: ...


class BaselineLoader(Protocol):
    """Load the fixed benchmark strategy for a match."""

    def __call__(self) -> Any: ...


class StageRunner(Protocol):
    """Stage runner contract used by the harness."""

    def run_match(
        self,
        strategy_a: EVMStrategyAdapter,
        strategy_b: Any,
        store_results: bool = False,
    ) -> Any: ...


class StageRunnerFactory(Protocol):
    """Build a stage runner for the requested stage."""

    def __call__(self, stage: str, n_workers: int | None) -> StageRunner: ...


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(value: str | None, *, fallback: str) -> str:
    if value is None:
        return fallback
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or fallback


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _json_dump(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _json_load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise HillClimbHarnessError(f"Invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise HillClimbHarnessError(f"Expected JSON object in {path}")
    return payload


def _tsv_field(value: str | None) -> str:
    if value is None:
        return ""
    return value.replace("\t", " ").replace("\n", " ").strip()


class _RunLock:
    """Portable directory-based lock for per-run artifact coordination."""

    def __init__(self, lock_path: Path, *, timeout_seconds: float = 10.0) -> None:
        self.lock_path = lock_path
        self.timeout_seconds = timeout_seconds

    def __enter__(self) -> "_RunLock":
        deadline = time.monotonic() + self.timeout_seconds
        while True:
            try:
                self.lock_path.mkdir(parents=False, exist_ok=False)
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise HillClimbHarnessError(
                        f"Timed out waiting for hill-climb run lock: {self.lock_path}"
                    ) from None
                time.sleep(0.01)

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self.lock_path.rmdir()
        except FileNotFoundError:
            return


class HillClimbHarness:
    """Run, record, and compare mean-edge strategy evaluations."""

    def __init__(
        self,
        *,
        artifact_root: Path | str = Path("artifacts/hill_climb"),
        n_workers: int | None = None,
        strategy_loader: StrategyLoader | None = None,
        baseline_loader: BaselineLoader | None = None,
        stage_runner_factory: StageRunnerFactory | None = None,
        protected_surface_checker: Any | None = None,
    ) -> None:
        self.artifact_root = Path(artifact_root)
        self.n_workers = n_workers
        self._strategy_loader = strategy_loader or self._load_strategy
        self._baseline_loader = baseline_loader or load_vanilla_strategy
        self._stage_runner_factory = stage_runner_factory or (
            lambda stage, n_workers: build_stage_runner(stage, n_workers=n_workers)
        )
        self._protected_surface_checker = protected_surface_checker

    def evaluate(
        self,
        *,
        run_id: str,
        stage: str,
        source_path: Path | str,
        label: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Evaluate a strategy source against the normalizer and persist artifacts."""
        normalized_run_id = _slug(run_id, fallback="run")
        stage_config = resolve_hill_climb_stage(stage)
        source_path = Path(source_path)
        run_dir = self._ensure_run_dir(
            normalized_run_id, source_path, target_stage=stage_config.name
        )

        source_text = self._read_source(source_path)
        source_sha256 = _sha256(source_text)
        snapshot_path = self._store_snapshot(run_dir, source_text, source_sha256)
        eval_id = self._reserve_evaluation_id(run_dir=run_dir, stage=stage_config.name)

        try:
            strategy = self._strategy_loader(source_text)
            result = self._stage_runner_factory(
                stage_config.name, self.n_workers
            ).run_match(
                strategy,
                self._baseline_loader(),
                store_results=True,
            )
            scorecard = compute_scorecard(result, stage=None)
            scorecard["run_metadata"]["stage"] = stage_config.name
            scorecard["run_metadata"]["seed_block"] = list(stage_config.seed_block)
            scorecard["gate"] = self._build_gate(
                mean_edge=float(scorecard["overall"]["mean_edge"]),
                stage_config=stage_config,
            )
            mean_edge = float(scorecard["overall"]["mean_edge"])
            strategy_name = strategy.get_name()
            incumbent_before = self._read_incumbent(run_dir, stage_config.name)
            selection = self._resolve_status(
                mean_edge,
                scorecard=scorecard,
                incumbent_before=incumbent_before,
                gate_passed=bool(scorecard["gate"]["passed"]),
            )
            summary = {
                "artifact_version": ARTIFACT_VERSION,
                "run_id": normalized_run_id,
                "eval_id": eval_id,
                "created_at": _utc_now(),
                "stage": stage_config.name,
                "stage_description": stage_config.description,
                "source_path": str(source_path.resolve()),
                "source_sha256": source_sha256,
                "snapshot_path": str(snapshot_path),
                "snapshot_relpath": str(snapshot_path.relative_to(run_dir)),
                "label": label,
                "description": description,
                "strategy_name": strategy_name,
                "status": selection.status,
                "mean_edge": mean_edge,
                "delta_vs_incumbent": selection.delta,
                "selection": {
                    "promotion_margin": selection.promotion_margin,
                    "rationale": selection.rationale,
                },
                "incumbent_before": incumbent_before,
                "scorecard": scorecard,
            }
        except Exception as exc:
            summary = {
                "artifact_version": ARTIFACT_VERSION,
                "run_id": normalized_run_id,
                "eval_id": eval_id,
                "created_at": _utc_now(),
                "stage": stage_config.name,
                "stage_description": stage_config.description,
                "source_path": str(source_path.resolve()),
                "source_sha256": source_sha256,
                "snapshot_path": str(snapshot_path),
                "snapshot_relpath": str(snapshot_path.relative_to(run_dir)),
                "label": label,
                "description": description,
                "strategy_name": None,
                "status": "invalid",
                "mean_edge": None,
                "delta_vs_incumbent": None,
                "incumbent_before": self._read_incumbent(run_dir, stage_config.name),
                "error": str(exc),
            }
            with self._run_lock(run_dir):
                self._append_result(run_dir, summary)
                self._write_state(
                    run_dir,
                    self._build_state_payload(
                        run_dir,
                        target_stage=stage_config.name,
                        existing_state=self._load_state_payload(
                            run_dir, require_current=True
                        ),
                    ),
                )
            raise HillClimbHarnessError(
                f"Evaluation failed for {source_path}: {exc}"
            ) from exc

        with self._run_lock(run_dir):
            self._append_result(run_dir, summary)
            if summary["status"] in {"seed", "keep"}:
                self._write_incumbent(run_dir, stage_config.name, summary)
            self._write_state(
                run_dir,
                self._build_state_payload(
                    run_dir,
                    target_stage=stage_config.name,
                    existing_state=self._load_state_payload(
                        run_dir, require_current=True
                    ),
                ),
            )
        return summary

    def get_stage_status(self, *, run_id: str, stage: str) -> StageStatus:
        """Return the latest and incumbent summaries for a run stage."""
        normalized_run_id = _slug(run_id, fallback="run")
        stage_config = resolve_hill_climb_stage(stage)
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        self._validate_current_run(run_dir)
        latest = self._read_latest(run_dir, stage_config.name)
        incumbent = self._read_incumbent(run_dir, stage_config.name)
        return StageStatus(
            run_id=normalized_run_id,
            stage=stage_config.name,
            incumbent=incumbent,
            latest=latest,
        )

    def get_run_state(self, *, run_id: str) -> RunStateStatus:
        """Return validated loop state and derived stop-rule guidance."""
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        self._validate_current_run(run_dir)
        results = self._read_results(run_dir)
        state = self._load_state_payload(run_dir, require_current=True)
        return self._run_state_status_from_payload(state, results)

    def update_run_state(
        self,
        *,
        run_id: str,
        current_target_stage: str | None = None,
        next_hypothesis: str | None = None,
        next_hypothesis_set: bool = False,
        run_mode: str | None = None,
        stop_rules: dict[str, int] | None = None,
    ) -> RunStateStatus:
        """Persist explicit loop-control metadata for an existing run."""
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")

        with self._run_lock(run_dir):
            self._validate_current_run(run_dir)
            results = self._read_results(run_dir)
            current_state = self._load_state_payload(run_dir, require_current=True)
            updated_state = dict(current_state)
            if current_target_stage is not None:
                updated_state["current_target_stage"] = current_target_stage
            if next_hypothesis_set:
                updated_state["next_hypothesis"] = next_hypothesis
            if run_mode is not None:
                updated_state["run_mode"] = run_mode
            if stop_rules is not None:
                updated_state["stop_rules"] = stop_rules
            updated_state["updated_at"] = _utc_now()
            self._validate_state(run_dir, updated_state, results)
            self._write_state(run_dir, updated_state)
        return self._run_state_status_from_payload(updated_state, results)

    def pull_best(self, *, run_id: str, stage: str, destination: Path | str) -> Path:
        """Copy the incumbent stage strategy snapshot into the destination path."""
        status = self.get_stage_status(run_id=run_id, stage=stage)
        if status.incumbent is None:
            raise HillClimbHarnessError(
                f"Run '{status.run_id}' has no incumbent recorded for stage '{status.stage}'"
            )
        snapshot_path = Path(status.incumbent["snapshot_path"])
        if not snapshot_path.exists():
            raise HillClimbHarnessError(
                f"Incumbent snapshot is missing on disk: {snapshot_path}"
            )
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(snapshot_path, destination_path)
        return destination_path

    def _ensure_run_dir(
        self, run_id: str, source_path: Path, *, target_stage: str
    ) -> Path:
        run_dir = self.artifact_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = run_dir / "run.json"
        if manifest_path.exists():
            self._validate_current_run(run_dir)
            manifest = _json_load(manifest_path)
            active_strategy_path = Path(manifest["active_strategy_path"]).resolve()
            if active_strategy_path != source_path.resolve():
                raise HillClimbHarnessError(
                    f"Run '{run_id}' is pinned to active strategy path {active_strategy_path}; "
                    f"refusing to evaluate alternate path {source_path.resolve()}"
                )
            return run_dir

        manifest = self._current_manifest_payload(
            run_id=run_id, source_path=source_path
        )
        self._write_manifest(run_dir, manifest)
        self._ensure_results_ledgers(run_dir)
        self._write_state(
            run_dir,
            self._default_state_payload(run_id=run_id, target_stage=target_stage),
        )
        self._write_next_eval_index(run_dir, 1)
        return run_dir

    def _read_source(self, source_path: Path) -> str:
        if not source_path.exists():
            raise HillClimbHarnessError(
                f"Strategy source does not exist: {source_path}"
            )
        if source_path.suffix != ".sol":
            raise HillClimbHarnessError(
                f"Hill-climb source must be a Solidity file: {source_path}"
            )
        return source_path.read_text()

    def _load_strategy(self, source_text: str) -> EVMStrategyAdapter:
        validator = SolidityValidator()
        validation = validator.validate(source_text)
        if not validation.valid:
            raise HillClimbHarnessError("; ".join(validation.errors))

        compiler = SolidityCompiler()
        compilation = compiler.compile(source_text)
        if not compilation.success:
            raise HillClimbHarnessError(
                "; ".join(compilation.errors or ["compile failed"])
            )
        if compilation.bytecode is None:
            raise HillClimbHarnessError(
                "Compiler returned success without deployment bytecode"
            )
        return EVMStrategyAdapter(bytecode=compilation.bytecode, abi=compilation.abi)

    def _run_lock(self, run_dir: Path) -> _RunLock:
        return _RunLock(run_dir / ".harness.lock")

    def _snapshot_dir(self, run_dir: Path) -> Path:
        return run_dir / "snapshots"

    def _snapshot_path(self, run_dir: Path, source_sha256: str) -> Path:
        return self._snapshot_dir(run_dir) / f"{source_sha256}.sol"

    def _write_snapshot_file(self, snapshot_path: Path, source_text: str) -> None:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(source_text)

    def _store_snapshot(
        self, run_dir: Path, source_text: str, source_sha256: str
    ) -> Path:
        snapshot_path = self._snapshot_path(run_dir, source_sha256)
        if snapshot_path.exists():
            return snapshot_path
        with self._run_lock(run_dir):
            if not snapshot_path.exists():
                self._write_snapshot_file(snapshot_path, source_text)
        return snapshot_path

    def _read_results(self, run_dir: Path) -> list[dict[str, Any]]:
        results_path = run_dir / "results.jsonl"
        if not results_path.exists():
            return []
        return [
            json.loads(line)
            for line in results_path.read_text().splitlines()
            if line.strip()
        ]

    def _next_eval_index(self, run_dir: Path) -> int:
        index_path = run_dir / NEXT_EVAL_INDEX_FILENAME
        if not index_path.exists():
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' is missing continuity file {NEXT_EVAL_INDEX_FILENAME!r}"
            )
        return self._parse_positive_int(
            index_path.read_text().strip(),
            path=index_path,
        )

    def _write_next_eval_index(self, run_dir: Path, next_index: int) -> None:
        (run_dir / NEXT_EVAL_INDEX_FILENAME).write_text(f"{next_index}\n")

    def _reserve_evaluation_id(self, *, run_dir: Path, stage: str) -> str:
        with self._run_lock(run_dir):
            eval_index = self._next_eval_index(run_dir)
            self._write_next_eval_index(run_dir, eval_index + 1)
            return f"{stage}_{eval_index:04d}"

    def _append_result(self, run_dir: Path, summary: dict[str, Any]) -> None:
        results_jsonl = run_dir / "results.jsonl"
        with results_jsonl.open("a") as handle:
            handle.write(json.dumps(summary, sort_keys=True) + "\n")
        self._append_results_row(run_dir, summary)

    def _resolve_status(
        self,
        mean_edge: float,
        scorecard: dict[str, Any],
        incumbent_before: dict[str, Any] | None,
        *,
        gate_passed: bool,
    ) -> SelectionDecision:
        if not gate_passed:
            return SelectionDecision(
                status="discard",
                delta=None,
                promotion_margin=None,
                rationale="stage gate failed",
            )
        if incumbent_before is None:
            return SelectionDecision(
                status="seed",
                delta=None,
                promotion_margin=None,
                rationale="no incumbent for this stage",
            )
        incumbent_mean_edge = float(incumbent_before["mean_edge"])
        delta = mean_edge - incumbent_mean_edge
        promotion_margin = self._promotion_margin(
            candidate_scorecard=scorecard,
            incumbent_before=incumbent_before,
        )
        if delta > promotion_margin:
            return SelectionDecision(
                status="keep",
                delta=delta,
                promotion_margin=promotion_margin,
                rationale=(
                    f"delta {delta:.6f} cleared promotion margin {promotion_margin:.6f}"
                ),
            )
        return SelectionDecision(
            status="discard",
            delta=delta,
            promotion_margin=promotion_margin,
            rationale=(
                f"delta {delta:.6f} did not clear promotion margin {promotion_margin:.6f}"
            ),
        )

    def _promotion_margin(
        self,
        *,
        candidate_scorecard: dict[str, Any],
        incumbent_before: dict[str, Any],
    ) -> float:
        candidate_overall = candidate_scorecard.get("overall", {})
        incumbent_overall = (
            incumbent_before.get("scorecard", {}).get("overall", {})
            if isinstance(incumbent_before.get("scorecard"), dict)
            else {}
        )
        candidate_se = self._edge_standard_error(candidate_overall)
        incumbent_se = self._edge_standard_error(incumbent_overall)
        if candidate_se is None or incumbent_se is None:
            return INCUMBENT_EPSILON
        return max(INCUMBENT_EPSILON, math.sqrt(candidate_se**2 + incumbent_se**2))

    def _edge_standard_error(self, overall: dict[str, Any]) -> float | None:
        edge_stddev = overall.get("edge_stddev")
        simulation_count = overall.get("simulation_count")
        if edge_stddev is None or simulation_count is None:
            return None
        n = int(simulation_count)
        if n <= 0:
            return None
        return float(edge_stddev) / math.sqrt(n)

    def _build_gate(self, *, mean_edge: float, stage_config: Any) -> dict[str, Any]:
        thresholds: dict[str, float] = {}
        failures: list[str] = []
        if stage_config.min_mean_edge is not None:
            thresholds["mean_edge"] = stage_config.min_mean_edge
            if mean_edge < stage_config.min_mean_edge:
                failures.append(
                    f"mean_edge={mean_edge:.6f} is below stage threshold "
                    f"{stage_config.min_mean_edge:.6f}"
                )
        return {
            "stage": stage_config.name,
            "thresholds": thresholds,
            "required_metric_fields": ["mean_edge"],
            "passed": not failures,
            "failures": failures,
        }

    def _incumbent_path(self, run_dir: Path, stage: str) -> Path:
        return run_dir / "incumbents" / f"{stage}.json"

    def _write_incumbent(
        self, run_dir: Path, stage: str, summary: dict[str, Any]
    ) -> None:
        incumbent_path = self._incumbent_path(run_dir, stage)
        incumbent_path.parent.mkdir(parents=True, exist_ok=True)
        incumbent_path.write_text(_json_dump(summary))

    def _read_incumbent(self, run_dir: Path, stage: str) -> dict[str, Any] | None:
        incumbent_path = self._incumbent_path(run_dir, stage)
        if not incumbent_path.exists():
            return None
        return json.loads(incumbent_path.read_text())

    def _read_latest(self, run_dir: Path, stage: str) -> dict[str, Any] | None:
        latest: dict[str, Any] | None = None
        for payload in self._read_results(run_dir):
            if payload["stage"] == stage:
                latest = payload
        return latest

    def _results_row(self, summary: dict[str, Any]) -> str:
        incumbent_before = summary.get("incumbent_before")
        incumbent_mean_edge = (
            ""
            if incumbent_before is None or incumbent_before.get("mean_edge") is None
            else f"{float(incumbent_before['mean_edge']):.6f}"
        )
        delta = summary.get("delta_vs_incumbent")
        delta_text = "" if delta is None else f"{float(delta):.6f}"
        mean_edge = summary.get("mean_edge")
        mean_edge_text = "" if mean_edge is None else f"{float(mean_edge):.6f}"
        return "\t".join(
            [
                summary["eval_id"],
                summary["stage"],
                summary["status"],
                mean_edge_text,
                incumbent_mean_edge,
                delta_text,
                _tsv_field(summary.get("strategy_name")),
                _tsv_field(summary.get("label")),
                _tsv_field(summary.get("description")),
                summary["snapshot_path"],
            ]
        )

    def _append_results_row(self, run_dir: Path, summary: dict[str, Any]) -> None:
        results_path = run_dir / "results.tsv"
        with results_path.open("a") as handle:
            handle.write(self._results_row(summary) + "\n")

    def _current_manifest_payload(
        self, *, run_id: str, source_path: Path
    ) -> dict[str, Any]:
        try:
            protected_surface_fingerprint = (
                self._protected_surface().current_fingerprint().to_payload()
            )
        except ProtectedSurfaceError as exc:
            raise HillClimbHarnessError(str(exc)) from exc
        return {
            "active_strategy_path": str(source_path.resolve()),
            "artifact_version": RUN_MANIFEST_VERSION,
            "continuity_counter": NEXT_EVAL_INDEX_FILENAME,
            "created_at": _utc_now(),
            "protected_surface_fingerprint": protected_surface_fingerprint,
            "results_jsonl": "results.jsonl",
            "results_tsv": "results.tsv",
            "run_id": run_id,
            "snapshot_dir": "snapshots",
            "snapshot_layout": SNAPSHOT_LAYOUT_VERSION,
            "state_path": "state.json",
        }

    def _write_manifest(self, run_dir: Path, manifest: dict[str, Any]) -> None:
        (run_dir / "run.json").write_text(_json_dump(manifest))

    def _default_state_payload(
        self, *, run_id: str, target_stage: str
    ) -> dict[str, Any]:
        return {
            "artifact_version": RUN_STATE_VERSION,
            "baseline_eval_id": None,
            "current_target_stage": target_stage,
            "incumbent_eval_ids": {},
            "last_completed_iteration": 0,
            "next_hypothesis": None,
            "run_id": run_id,
            "run_mode": "foreground",
            "stop_rules": dict(DEFAULT_STOP_RULES),
            "updated_at": _utc_now(),
        }

    def _build_state_payload(
        self,
        run_dir: Path,
        *,
        target_stage: str,
        existing_state: dict[str, Any],
    ) -> dict[str, Any]:
        results = self._read_results(run_dir)
        baseline_summary = next(
            (summary for summary in results if summary.get("status") != "invalid"),
            None,
        )
        baseline_eval_id = (
            None if baseline_summary is None else baseline_summary["eval_id"]
        )
        incumbent_eval_ids: dict[str, str] = {}
        for summary in results:
            if summary["status"] in {"seed", "keep"}:
                incumbent_eval_ids[summary["stage"]] = summary["eval_id"]
        return {
            "artifact_version": RUN_STATE_VERSION,
            "baseline_eval_id": baseline_eval_id,
            "current_target_stage": existing_state.get(
                "current_target_stage", target_stage
            ),
            "incumbent_eval_ids": incumbent_eval_ids,
            "last_completed_iteration": len(results),
            "next_hypothesis": existing_state.get("next_hypothesis"),
            "run_id": run_dir.name,
            "run_mode": existing_state.get("run_mode", "foreground"),
            "stop_rules": existing_state.get("stop_rules", dict(DEFAULT_STOP_RULES)),
            "updated_at": _utc_now(),
        }

    def _write_state(self, run_dir: Path, state: dict[str, Any]) -> None:
        (run_dir / "state.json").write_text(_json_dump(state))

    def _load_state_payload(
        self, run_dir: Path, *, require_current: bool
    ) -> dict[str, Any]:
        state_path = run_dir / "state.json"
        if not state_path.exists():
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' is missing state.json. "
                "Retained runs without the current hill-climb artifact layout are unsupported; "
                "start a fresh run instead."
            )
        state = _json_load(state_path)
        if require_current and state.get("artifact_version") != RUN_STATE_VERSION:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has unsupported state version "
                f"{state.get('artifact_version')!r}; expected {RUN_STATE_VERSION!r}. "
                "Retained runs without the current hill-climb artifact layout are unsupported; "
                "start a fresh run instead."
            )
        return state

    def _ensure_results_ledgers(self, run_dir: Path) -> None:
        results_jsonl = run_dir / "results.jsonl"
        if not results_jsonl.exists():
            results_jsonl.write_text("")
        results_tsv = run_dir / "results.tsv"
        if not results_tsv.exists():
            results_tsv.write_text(RESULTS_HEADER)

    def _validate_results_ledgers(self, run_dir: Path) -> None:
        results_jsonl = run_dir / "results.jsonl"
        if not results_jsonl.exists():
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' is missing results.jsonl"
            )
        results_tsv = run_dir / "results.tsv"
        if not results_tsv.exists():
            raise HillClimbHarnessError(f"Run '{run_dir.name}' is missing results.tsv")
        header = results_tsv.read_text().splitlines()
        if not header or header[0] != RESULTS_HEADER.rstrip("\n"):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has malformed results.tsv header"
            )

    def _parse_positive_int(self, raw_value: str, *, path: Path) -> int:
        try:
            value = int(raw_value)
        except ValueError as exc:
            raise HillClimbHarnessError(
                f"Expected integer in {path}, found {raw_value!r}"
            ) from exc
        if value <= 0:
            raise HillClimbHarnessError(
                f"Expected positive integer in {path}, found {value}"
            )
        return value

    def _parse_eval_id(self, eval_id: str) -> tuple[str, int]:
        match = re.fullmatch(r"([a-z0-9-]+)_(\d{4})", eval_id)
        if match is None:
            raise HillClimbHarnessError(f"Invalid eval_id format: {eval_id!r}")
        stage, raw_index = match.groups()
        return stage, int(raw_index)

    def _validate_current_run(self, run_dir: Path) -> None:
        manifest_path = run_dir / "run.json"
        if not manifest_path.exists():
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' is missing run.json. "
                "Retained runs without the current hill-climb artifact layout are unsupported; "
                "start a fresh run instead."
            )
        manifest = _json_load(manifest_path)
        if manifest.get("artifact_version") != RUN_MANIFEST_VERSION:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has unsupported manifest version "
                f"{manifest.get('artifact_version')!r}; expected {RUN_MANIFEST_VERSION!r}. "
                "Retained runs without the current hill-climb artifact layout are unsupported; "
                "start a fresh run instead."
            )
        required_fields = {
            "active_strategy_path",
            "artifact_version",
            "continuity_counter",
            "created_at",
            "results_jsonl",
            "results_tsv",
            "run_id",
            "snapshot_dir",
            "snapshot_layout",
            "state_path",
        }
        missing = sorted(required_fields - set(manifest))
        if missing:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' manifest is missing required fields: {', '.join(missing)}"
            )
        if manifest["run_id"] != run_dir.name:
            raise HillClimbHarnessError(
                f"Run manifest run_id {manifest['run_id']!r} does not match directory {run_dir.name!r}"
            )
        for field, expected in (
            ("results_jsonl", "results.jsonl"),
            ("results_tsv", "results.tsv"),
            ("snapshot_dir", "snapshots"),
            ("state_path", "state.json"),
        ):
            if manifest[field] != expected:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' must use {expected!r} for manifest field {field!r}"
                )
        if manifest["snapshot_layout"] != SNAPSHOT_LAYOUT_VERSION:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has unsupported snapshot layout "
                f"{manifest['snapshot_layout']!r}; expected {SNAPSHOT_LAYOUT_VERSION!r}"
            )
        if manifest["continuity_counter"] != NEXT_EVAL_INDEX_FILENAME:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' must use {NEXT_EVAL_INDEX_FILENAME!r} as its continuity counter"
            )
        active_strategy_path = Path(manifest["active_strategy_path"])
        if active_strategy_path.suffix != ".sol":
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has invalid active_strategy_path {active_strategy_path!s}"
            )
        self._validate_results_ledgers(run_dir)
        results = self._read_results(run_dir)
        self._validate_results(run_dir, results)
        self._validate_continuity_files(run_dir, results)
        state = self._load_state_payload(run_dir, require_current=True)
        self._validate_state(run_dir, state, results)
        self._validate_snapshots(run_dir, results)
        try:
            self._protected_surface().verify_recorded_fingerprint(
                manifest.get("protected_surface_fingerprint"),
                run_id=run_dir.name,
            )
        except ProtectedSurfaceError as exc:
            raise HillClimbHarnessError(str(exc)) from exc

    def _protected_surface(self) -> Any:
        if self._protected_surface_checker is None:
            self._protected_surface_checker = ProtectedSurfaceChecker.discover()
        return self._protected_surface_checker

    def _validate_results(self, run_dir: Path, results: list[dict[str, Any]]) -> None:
        seen_eval_ids: set[str] = set()
        expected_index = 1
        for summary in results:
            eval_id = summary.get("eval_id")
            stage = summary.get("stage")
            if not isinstance(eval_id, str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has a result without a string eval_id"
                )
            if not isinstance(stage, str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has result {eval_id!r} without a stage"
                )
            if stage not in HILL_CLIMB_STAGES:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has result {eval_id!r} with unknown stage {stage!r}"
                )
            if eval_id in seen_eval_ids:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' contains duplicate eval_id {eval_id!r} in results.jsonl"
                )
            seen_eval_ids.add(eval_id)
            eval_stage, index = self._parse_eval_id(eval_id)
            if eval_stage != stage:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval_id {eval_id!r} that does not match stage {stage!r}"
                )
            if index != expected_index:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has non-contiguous eval ids: expected index "
                    f"{expected_index:04d}, found {eval_id!r}"
                )
            expected_index += 1

    def _validate_continuity_files(
        self, run_dir: Path, results: list[dict[str, Any]]
    ) -> None:
        legacy_counter = run_dir / LEGACY_NEXT_EVAL_ID_FILENAME
        if legacy_counter.exists():
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' still has obsolete continuity file {LEGACY_NEXT_EVAL_ID_FILENAME!r}. "
                "Retained runs with the old continuity file are unsupported; "
                "start a fresh run instead."
            )
        counter_path = run_dir / NEXT_EVAL_INDEX_FILENAME
        if not counter_path.exists():
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' is missing continuity file {NEXT_EVAL_INDEX_FILENAME!r}"
            )
        next_eval_index = self._parse_positive_int(
            counter_path.read_text().strip(), path=counter_path
        )
        expected_next = len(results) + 1
        if next_eval_index != expected_next:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has stale {NEXT_EVAL_INDEX_FILENAME!r}: "
                f"expected {expected_next}, found {next_eval_index}"
            )

    def _validate_state(
        self,
        run_dir: Path,
        state: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> None:
        required_fields = {
            "artifact_version",
            "baseline_eval_id",
            "current_target_stage",
            "incumbent_eval_ids",
            "last_completed_iteration",
            "next_hypothesis",
            "run_id",
            "run_mode",
            "stop_rules",
            "updated_at",
        }
        missing = sorted(required_fields - set(state))
        if missing:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' state is missing required fields: {', '.join(missing)}"
            )
        if state["run_id"] != run_dir.name:
            raise HillClimbHarnessError(
                f"Run state run_id {state['run_id']!r} does not match directory {run_dir.name!r}"
            )
        if state["current_target_stage"] not in HILL_CLIMB_STAGES:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has unknown current_target_stage {state['current_target_stage']!r}"
            )
        if not isinstance(state["incumbent_eval_ids"], dict):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' state field incumbent_eval_ids must be an object"
            )
        if not isinstance(state["stop_rules"], dict):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' state field stop_rules must be an object"
            )
        if state["run_mode"] not in {"foreground", "background"}:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has unsupported run_mode {state['run_mode']!r}"
            )
        if state["next_hypothesis"] is not None and not isinstance(
            state["next_hypothesis"], str
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' state field next_hypothesis must be null or a string"
            )
        for key, minimum in DEFAULT_STOP_RULES.items():
            raw_value = state["stop_rules"].get(key)
            if not isinstance(raw_value, int) or raw_value < minimum:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' stop_rules[{key!r}] must be an integer >= {minimum}"
                )
        baseline_summary = next(
            (summary for summary in results if summary.get("status") != "invalid"),
            None,
        )
        expected_baseline = (
            None if baseline_summary is None else baseline_summary["eval_id"]
        )
        if state["baseline_eval_id"] != expected_baseline:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has stale baseline_eval_id: expected {expected_baseline!r}, "
                f"found {state['baseline_eval_id']!r}"
            )
        if state["last_completed_iteration"] != len(results):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has stale last_completed_iteration: expected {len(results)}, "
                f"found {state['last_completed_iteration']}"
            )
        expected_incumbents: dict[str, str] = {}
        for summary in results:
            if summary["status"] in {"seed", "keep"}:
                expected_incumbents[summary["stage"]] = summary["eval_id"]
        if state["incumbent_eval_ids"] != expected_incumbents:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has stale incumbent_eval_ids in state.json"
            )

    def _run_state_status_from_payload(
        self,
        state: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> RunStateStatus:
        guidance = self._build_loop_guidance(state, results)
        return RunStateStatus(
            run_id=state["run_id"],
            baseline_eval_id=state["baseline_eval_id"],
            current_target_stage=state["current_target_stage"],
            incumbent_eval_ids=dict(state["incumbent_eval_ids"]),
            last_completed_iteration=state["last_completed_iteration"],
            next_hypothesis=state["next_hypothesis"],
            run_mode=state["run_mode"],
            stop_rules=dict(state["stop_rules"]),
            updated_at=state["updated_at"],
            guidance=guidance,
        )

    def _build_loop_guidance(
        self,
        state: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> LoopGuidance:
        target_stage = state["current_target_stage"]
        streak = self._non_improving_streak(results, stage=target_stage)
        stop_rules = state["stop_rules"]
        if streak >= stop_rules["stop_after_non_improving_iterations"]:
            return LoopGuidance(
                non_improving_streak=streak,
                action="stop",
                message=(
                    "stop now "
                    f"({streak} consecutive non-improving {target_stage} evaluations; "
                    f"threshold {stop_rules['stop_after_non_improving_iterations']})"
                ),
            )
        if streak >= stop_rules["pivot_after_non_improving_iterations"]:
            return LoopGuidance(
                non_improving_streak=streak,
                action="pivot",
                message=(
                    "pivot now "
                    f"({streak} consecutive non-improving {target_stage} evaluations; "
                    f"threshold {stop_rules['pivot_after_non_improving_iterations']})"
                ),
            )
        if streak >= stop_rules["refine_after_non_improving_iterations"]:
            return LoopGuidance(
                non_improving_streak=streak,
                action="refine",
                message=(
                    "refine now "
                    f"({streak} consecutive non-improving {target_stage} evaluations; "
                    f"threshold {stop_rules['refine_after_non_improving_iterations']})"
                ),
            )
        return LoopGuidance(
            non_improving_streak=streak,
            action="continue",
            message=(
                "continue "
                f"(refine in {stop_rules['refine_after_non_improving_iterations'] - streak}, "
                f"pivot in {stop_rules['pivot_after_non_improving_iterations'] - streak}, "
                f"stop in {stop_rules['stop_after_non_improving_iterations'] - streak})"
            ),
        )

    def _non_improving_streak(
        self, results: list[dict[str, Any]], *, stage: str
    ) -> int:
        streak = 0
        for summary in reversed(results):
            if summary["stage"] != stage:
                continue
            if summary["status"] in {"seed", "keep"}:
                return streak
            streak += 1
        return streak

    def _validate_snapshots(self, run_dir: Path, results: list[dict[str, Any]]) -> None:
        snapshot_dir = self._snapshot_dir(run_dir).resolve()
        for summary in results:
            snapshot_path = Path(summary["snapshot_path"])
            if not snapshot_path.exists():
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' references missing snapshot {snapshot_path}"
                )
            if snapshot_path.resolve().parent != snapshot_dir:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' references snapshot outside {snapshot_dir}: {snapshot_path}"
                )
            relpath = summary.get("snapshot_relpath")
            if (
                relpath is not None
                and (run_dir / relpath).resolve() != snapshot_path.resolve()
            ):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has mismatched snapshot_relpath for {summary['eval_id']}"
                )
            source_sha256 = summary.get("source_sha256")
            if source_sha256 is None:
                continue
            if snapshot_path.name != f"{source_sha256}.sol":
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has snapshot name/hash mismatch for {summary['eval_id']}"
                )
            if _sha256(snapshot_path.read_text()) != source_sha256:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has snapshot content/hash mismatch for {summary['eval_id']}"
                )
