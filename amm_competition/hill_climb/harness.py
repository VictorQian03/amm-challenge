"""Thin append-only harness for hill-climb evaluation and read surfaces."""

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
from amm_competition.hill_climb.stages import (
    HILL_CLIMB_STAGES,
    build_stage_runner,
    resolve_hill_climb_stage,
)

DEFAULT_ARTIFACT_ROOT = Path("artifacts/hill_climb")
DEFAULT_STRATEGY_PATH = Path("contracts/src/StarterStrategy.sol")
RUN_MANIFEST_VERSION = "hill_climb.run.v2"
RUN_RESULT_VERSION = "hill_climb.eval.v1"
RUN_HISTORY_VERSION = "hill_climb.history.v1"
CROSS_RUN_INDEX_VERSION = "hill_climb.index.v1"
SNAPSHOT_LAYOUT_VERSION = "content_addressed.v1"
RETAINED_LAYOUT_VERSION = "consolidated.v1"
INCUMBENT_EPSILON = 1e-9
RUN_STATUSES = frozenset({"seed", "keep", "discard", "invalid"})
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
WORKER_RUN_ID_RE = re.compile(r"(?:^|-)w\d+(?:-|$)")
LEGACY_RETAINED_SURFACES = (
    "results.tsv",
    "history.jsonl",
    "incumbents",
    ".next_eval_index",
)
PROFILE_FIELDS = (
    "mean_edge",
    "retail_edge",
    "arb_edge",
    "arb_loss_to_retail_gain",
    "time_weighted_bid_fee",
    "time_weighted_ask_fee",
    "time_weighted_mean_fee",
    "quote_selectivity_ratio",
    "max_fee_jump",
)


class HillClimbHarnessError(RuntimeError):
    """Raised when hill-climb setup or execution is invalid."""


def _safe_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, (int, float)):
        return None
    converted = float(value)
    if not math.isfinite(converted):
        return None
    return converted


def _delta(current: float | None, baseline: float | None) -> float | None:
    if current is None or baseline is None:
        return None
    return current - baseline


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _slug(value: str | None, *, fallback: str) -> str:
    if value is None:
        return fallback
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or fallback


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _snapshot_relpath(source_sha256: str) -> str:
    return f"snapshots/{source_sha256}.sol"


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


class HillClimbHarness:
    """Run, record, and compare strategy evaluations without planning constraints."""

    def __init__(
        self,
        *,
        artifact_root: Path | str = DEFAULT_ARTIFACT_ROOT,
        n_workers: int | None = None,
        strategy_loader: StrategyLoader | None = None,
        baseline_loader: BaselineLoader | None = None,
        stage_runner_factory: StageRunnerFactory | None = None,
        protected_surface_checker: Any | None = None,
    ) -> None:
        self.artifact_root = Path(artifact_root)
        self.n_workers = n_workers
        self._strategy_loader = strategy_loader or EVMStrategyAdapter.from_source
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
        replay_reason: str | None = None,
    ) -> dict[str, Any]:
        """Evaluate a strategy source against the fixed normalizer and persist artifacts."""
        self._protected_surface().ensure_runtime_eval_allowed()

        normalized_run_id = _slug(run_id, fallback="run")
        self._assert_retained_run_id_allowed(normalized_run_id)
        stage_config = resolve_hill_climb_stage(stage)
        source_path = Path(source_path)
        if not source_path.exists():
            raise HillClimbHarnessError(f"Strategy file not found: {source_path}")

        run_dir = self._ensure_run_dir(normalized_run_id)
        source_text = self._read_source(source_path)
        source_sha256 = _sha256(source_text)
        created_at = _utc_now()

        with self._run_lock(run_dir):
            manifest = self._load_or_create_manifest(run_dir, run_id=normalized_run_id)
            results = self._read_results(run_dir, manifest=manifest)
            self._reject_duplicate_stage_source(
                results=results,
                stage=stage_config.name,
                source_sha256=source_sha256,
                replay_reason=replay_reason,
            )
            self._store_snapshot(run_dir, source_text, source_sha256)
            eval_id = self._next_evaluation_id(results, stage=stage_config.name)
            incumbent_before = self._read_incumbent(
                run_dir,
                stage_config.name,
                results,
            )
            summary_base = self._evaluation_summary_base(
                run_id=normalized_run_id,
                eval_id=eval_id,
                stage=stage_config.name,
                source_path=source_path,
                source_sha256=source_sha256,
                label=label,
                description=description,
                replay_reason=replay_reason,
                created_at=created_at,
                incumbent_before=incumbent_before,
            )

            try:
                strategy, scorecard, gate = self._run_stage_evaluation(
                    stage_config=stage_config,
                    source_text=source_text,
                )
                mean_edge = float(scorecard["overall"]["mean_edge"])
                selection = self._resolve_status(
                    mean_edge,
                    scorecard=scorecard,
                    incumbent_before=incumbent_before,
                    gate_passed=bool(gate["passed"]),
                )
                summary = {
                    **summary_base,
                    "strategy_name": strategy.get_name(),
                    "status": selection.status,
                    "mean_edge": mean_edge,
                    "delta_vs_incumbent": selection.delta,
                    "selection": {
                        "promotion_margin": selection.promotion_margin,
                        "rationale": selection.rationale,
                    },
                    "gate": gate,
                    "scorecard": scorecard,
                    "derived_analysis": self._build_derived_analysis(
                        scorecard=scorecard,
                        incumbent_before=incumbent_before,
                    ),
                }
            except Exception as exc:
                summary = {
                    **summary_base,
                    "strategy_name": None,
                    "status": "invalid",
                    "mean_edge": None,
                    "delta_vs_incumbent": None,
                    "selection": {
                        "promotion_margin": None,
                        "rationale": "evaluation failed before comparison",
                    },
                    "gate": {
                        "stage": stage_config.name,
                        "thresholds": {},
                        "required_metric_fields": [],
                        "passed": False,
                        "failures": [str(exc)],
                    },
                    "error": str(exc),
                    "derived_analysis": self._build_invalid_analysis(str(exc)),
                }
                self._append_result(run_dir, summary)
                self._sync_derived_views(
                    run_dir=run_dir,
                    manifest=manifest,
                    results=[*results, summary],
                )
                raise HillClimbHarnessError(
                    f"Evaluation failed for {source_path}: {exc}"
                ) from exc

            self._append_result(run_dir, summary)
            self._sync_derived_views(
                run_dir=run_dir,
                manifest=manifest,
                results=[*results, summary],
            )
            return summary

    def list_runs(
        self, *, allow_protected_surface_drift: bool = False
    ) -> dict[str, Any]:
        """Return the cross-run catalog for all hill-climb runs."""
        del allow_protected_surface_drift
        return self._write_cross_run_index()

    def get_run_status(
        self,
        *,
        run_id: str,
        stage: str | None = None,
        allow_protected_surface_drift: bool = False,
    ) -> dict[str, Any]:
        """Return stage status for one run, optionally scoped to a single stage."""
        context = self._read_run_context(
            run_id=run_id,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        requested_stages = (
            [resolve_hill_climb_stage(stage).name]
            if stage is not None
            else self._status_stage_names(context["results"])
        )
        return {
            "run_id": context["manifest"]["run_id"],
            "created_at": context["manifest"]["created_at"],
            "updated_at": context["manifest"]["updated_at"],
            "eval_count": context["manifest"]["eval_count"],
            "snapshot_count": context["manifest"]["snapshot_count"],
            "warnings": context["warnings"],
            "latest": self._compact_summary(context["results"][-1]) if context["results"] else None,
            "stages": {
                stage_name: {
                    "incumbent": self._compact_summary(
                        self._read_incumbent(
                            context["run_dir"],
                            stage_name,
                            context["results"],
                        )
                    ),
                    "best_raw": self._compact_summary(
                        self._best_stage_raw(context["results"], stage=stage_name)
                    ),
                    "latest": self._compact_summary(
                        self._read_latest(context["results"], stage=stage_name)
                    ),
                }
                for stage_name in requested_stages
            },
        }

    def get_history(
        self,
        *,
        run_id: str,
        allow_protected_surface_drift: bool = False,
    ) -> list[dict[str, Any]]:
        """Return the compact history view for one run."""
        context = self._read_run_context(
            run_id=run_id,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        return self._build_history(context["results"])

    def get_evaluation(
        self,
        *,
        run_id: str,
        eval_id: str,
        allow_protected_surface_drift: bool = False,
    ) -> dict[str, Any]:
        """Return one evaluation summary by id."""
        context = self._read_run_context(
            run_id=run_id,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        for summary in context["results"]:
            if summary["eval_id"] == eval_id:
                return summary
        raise HillClimbHarnessError(
            f"Run '{context['manifest']['run_id']}' has no evaluation {eval_id!r}"
        )

    def pull_best(
        self,
        *,
        run_id: str,
        stage: str,
        destination: Path | str,
        allow_protected_surface_drift: bool = False,
    ) -> Path:
        """Restore the current stage incumbent snapshot to a destination path."""
        context = self._read_run_context(
            run_id=run_id,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        stage_name = resolve_hill_climb_stage(stage).name
        incumbent = self._read_incumbent(
            context["run_dir"],
            stage_name,
            context["results"],
        )
        if incumbent is None:
            raise HillClimbHarnessError(
                f"Run '{context['manifest']['run_id']}' has no incumbent for stage {stage_name!r}"
            )
        snapshot_relpath = incumbent.get("snapshot_relpath")
        if not isinstance(snapshot_relpath, str) or not snapshot_relpath:
            raise HillClimbHarnessError(
                f"Incumbent {incumbent['eval_id']} is missing snapshot_relpath"
            )
        source_path = context["run_dir"] / snapshot_relpath
        if not source_path.exists():
            raise HillClimbHarnessError(f"Missing snapshot file: {source_path}")
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)
        return destination_path

    def compare_profiles(
        self,
        *,
        stage: str,
        baseline_summary: dict[str, Any] | None = None,
        candidate_summary: dict[str, Any] | None = None,
        baseline_source_path: Path | str | None = None,
        candidate_source_path: Path | str | None = None,
        anchor_summary: dict[str, Any] | None = None,
        anchor_source_path: Path | str | None = None,
    ) -> dict[str, Any]:
        """Compare stage-aligned profiles from stored evals or ad hoc sources."""
        baseline_profile = self._resolve_profile_input(
            stage=stage,
            summary=baseline_summary,
            source_path=baseline_source_path,
        )
        candidate_profile = self._resolve_profile_input(
            stage=stage,
            summary=candidate_summary,
            source_path=candidate_source_path,
        )
        payload = {
            "stage": stage,
            "baseline": baseline_profile,
            "candidate": candidate_profile,
            "candidate_vs_baseline": self._compare_profile_maps(
                candidate_profile["profile"],
                baseline_profile["profile"],
            ),
        }
        if anchor_summary is not None or anchor_source_path is not None:
            anchor_profile = self._resolve_profile_input(
                stage=stage,
                summary=anchor_summary,
                source_path=anchor_source_path,
            )
            payload["anchor"] = anchor_profile
            payload["candidate_vs_anchor"] = self._compare_profile_maps(
                candidate_profile["profile"],
                anchor_profile["profile"],
            )
            payload["baseline_vs_anchor"] = self._compare_profile_maps(
                baseline_profile["profile"],
                anchor_profile["profile"],
            )
        return payload

    def _status_stage_names(self, results: list[dict[str, Any]]) -> list[str]:
        stages = [stage for stage in HILL_CLIMB_STAGES if self._read_latest(results, stage=stage)]
        return stages or ["screen"]

    def _compact_summary(self, summary: dict[str, Any] | None) -> dict[str, Any] | None:
        if summary is None:
            return None
        derived = summary.get("derived_analysis", {})
        profile = derived.get("profile", {}) if isinstance(derived, dict) else {}
        failure = (
            derived.get("failure_signature", {}) if isinstance(derived, dict) else {}
        )
        return {
            "eval_id": summary["eval_id"],
            "stage": summary["stage"],
            "status": summary["status"],
            "mean_edge": summary.get("mean_edge"),
            "label": summary.get("label"),
            "strategy_name": summary.get("strategy_name"),
            "incumbent_before_eval_id": summary.get("incumbent_before_eval_id"),
            "selection": summary.get("selection"),
            "gate": summary.get("gate"),
            "profile": profile,
            "failure_tags": list(failure.get("tags", [])),
        }

    def _read_run_context(
        self,
        *,
        run_id: str,
        allow_protected_surface_drift: bool = False,
    ) -> dict[str, Any]:
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        warnings: list[str] = []
        manifest = self._load_manifest(
            run_dir,
            run_id=normalized_run_id,
            allow_protected_surface_drift=allow_protected_surface_drift,
            warnings=warnings,
        )
        results = self._read_results(run_dir, manifest=manifest)
        return {
            "run_dir": run_dir,
            "manifest": manifest,
            "results": results,
            "warnings": warnings,
        }

    def _read_source(self, source_path: Path) -> str:
        try:
            return source_path.read_text()
        except OSError as exc:
            raise HillClimbHarnessError(f"Unable to read strategy source {source_path}") from exc

    def _ensure_run_dir(self, run_id: str) -> Path:
        run_dir = self.artifact_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _run_lock(self, run_dir: Path) -> _RunLock:
        return _RunLock(run_dir / ".lock")

    def _manifest_path(self, run_dir: Path) -> Path:
        return run_dir / "run.json"

    def _results_path(self, run_dir: Path) -> Path:
        return run_dir / "results.jsonl"

    def _snapshot_dir(self, run_dir: Path) -> Path:
        return run_dir / "snapshots"

    def _snapshot_path(self, run_dir: Path, source_sha256: str) -> Path:
        return self._snapshot_dir(run_dir) / f"{source_sha256}.sol"

    def _load_or_create_manifest(self, run_dir: Path, *, run_id: str) -> dict[str, Any]:
        manifest_path = self._manifest_path(run_dir)
        if manifest_path.exists():
            return self._load_manifest(run_dir, run_id=run_id, warnings=[])

        self._snapshot_dir(run_dir).mkdir(parents=True, exist_ok=True)
        self._results_path(run_dir).write_text("")
        created_at = _utc_now()

        manifest = {
            "artifact_version": RUN_MANIFEST_VERSION,
            "run_id": run_id,
            "created_at": created_at,
            "updated_at": created_at,
            "snapshot_layout": SNAPSHOT_LAYOUT_VERSION,
            "persistence_policy": RETAINED_LAYOUT_VERSION,
            "protected_surface_fingerprint": self._protected_surface()
            .current_fingerprint()
            .to_payload(),
            "latest_eval_id": None,
            "latest_stage": None,
            "eval_count": 0,
            "snapshot_count": 0,
        }
        manifest_path.write_text(_json_dump(manifest))
        return manifest

    def _load_manifest(
        self,
        run_dir: Path,
        *,
        run_id: str,
        allow_protected_surface_drift: bool = False,
        warnings: list[str],
    ) -> dict[str, Any]:
        manifest = _json_load(self._manifest_path(run_dir))
        required_fields = {
            "artifact_version",
            "run_id",
            "created_at",
            "updated_at",
            "snapshot_layout",
            "persistence_policy",
            "protected_surface_fingerprint",
            "latest_eval_id",
            "latest_stage",
            "eval_count",
            "snapshot_count",
        }
        missing = sorted(field for field in required_fields if field not in manifest)
        if missing:
            raise HillClimbHarnessError(
                f"Run '{run_id}' manifest is missing required fields: {', '.join(missing)}"
            )
        self._assert_retained_run_id_allowed(run_id)
        if manifest["run_id"] != run_id:
            raise HillClimbHarnessError(
                f"Run directory {run_dir.name!r} contains mismatched manifest run_id {manifest['run_id']!r}"
            )
        if manifest["artifact_version"] != RUN_MANIFEST_VERSION:
            raise HillClimbHarnessError(
                f"Run '{run_id}' manifest has unsupported artifact_version "
                f"{manifest['artifact_version']!r}; expected {RUN_MANIFEST_VERSION!r}"
            )
        if manifest["snapshot_layout"] != SNAPSHOT_LAYOUT_VERSION:
            raise HillClimbHarnessError(
                f"Run '{run_id}' manifest has unsupported snapshot_layout "
                f"{manifest['snapshot_layout']!r}; expected {SNAPSHOT_LAYOUT_VERSION!r}"
            )
        if manifest["persistence_policy"] != RETAINED_LAYOUT_VERSION:
            raise HillClimbHarnessError(
                f"Run '{run_id}' manifest has unsupported persistence_policy "
                f"{manifest['persistence_policy']!r}; expected {RETAINED_LAYOUT_VERSION!r}"
            )
        for field in ("created_at", "updated_at"):
            if not isinstance(manifest[field], str) or not manifest[field]:
                raise HillClimbHarnessError(
                    f"Run '{run_id}' manifest field {field!r} must be a non-empty string"
                )
        for field in ("eval_count", "snapshot_count"):
            value = manifest.get(field)
            if not isinstance(value, int) or value < 0:
                raise HillClimbHarnessError(
                    f"Run '{run_id}' manifest field {field!r} must be a non-negative integer"
                )
        self._validate_run_layout(run_dir)
        try:
            self._protected_surface().verify_recorded_fingerprint(
                manifest.get("protected_surface_fingerprint"),
                run_id=run_id,
            )
        except ProtectedSurfaceError as exc:
            if not allow_protected_surface_drift:
                raise HillClimbHarnessError(str(exc)) from exc
            warnings.append(str(exc))
        return manifest

    def _validate_run_layout(self, run_dir: Path) -> None:
        issues: list[str] = []
        if not self._results_path(run_dir).is_file():
            issues.append("missing results.jsonl")
        if not self._snapshot_dir(run_dir).is_dir():
            issues.append("missing snapshots/")
        legacy_surfaces = []
        for name in LEGACY_RETAINED_SURFACES:
            legacy_path = run_dir / name
            if legacy_path.exists():
                legacy_surfaces.append(f"{name}/" if legacy_path.is_dir() else name)
        if legacy_surfaces:
            issues.append(
                "unexpected legacy retained artifacts: " + ", ".join(sorted(legacy_surfaces))
            )
        if issues:
            raise HillClimbHarnessError(
                self._corrupted_run_message(run_dir, "; ".join(issues))
            )

    def _read_results(self, run_dir: Path, *, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        results_path = self._results_path(run_dir)
        results: list[dict[str, Any]] = []
        for raw_line in results_path.read_text().splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise HillClimbHarnessError(
                    f"Invalid JSON in {results_path}: {exc.msg}"
                ) from exc
            if not isinstance(payload, dict):
                raise HillClimbHarnessError(f"Expected JSON object in {results_path}")
            results.append(payload)
        self._validate_results(run_dir, results, manifest=manifest)
        return results

    def _validate_results(
        self,
        run_dir: Path,
        results: list[dict[str, Any]],
        *,
        manifest: dict[str, Any],
    ) -> None:
        seen_eval_ids: set[str] = set()
        expected_snapshots: set[str] = set()
        for index, summary in enumerate(results, start=1):
            eval_id = self._validate_result_summary(
                run_dir,
                summary,
                seen_eval_ids=seen_eval_ids,
            )
            seen_eval_ids.add(eval_id)
            expected_eval_id = f"{summary['stage']}_{index:04d}"
            if eval_id != expected_eval_id:
                raise HillClimbHarnessError(
                    self._corrupted_run_message(
                        run_dir,
                        f"results.jsonl entry {eval_id} breaks retained eval ordering; expected {expected_eval_id}",
                    )
                )
            expected_snapshots.add(summary["snapshot_relpath"].removeprefix("snapshots/"))
        if manifest.get("eval_count") != len(results):
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    "manifest eval_count does not match results.jsonl",
                )
            )
        latest = results[-1] if results else None
        expected_latest_eval_id = None if latest is None else latest["eval_id"]
        expected_latest_stage = None if latest is None else latest["stage"]
        if manifest.get("latest_eval_id") != expected_latest_eval_id:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    "manifest latest_eval_id does not match results.jsonl",
                )
            )
        if manifest.get("latest_stage") != expected_latest_stage:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    "manifest latest_stage does not match results.jsonl",
                )
            )
        actual_snapshots = {
            path.name
            for path in self._snapshot_dir(run_dir).iterdir()
            if path.is_file()
        }
        unexpected_snapshots = sorted(actual_snapshots - expected_snapshots)
        if unexpected_snapshots:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    "snapshots/ contains unreferenced files: " + ", ".join(unexpected_snapshots),
                )
            )
        if manifest.get("snapshot_count") != len(expected_snapshots):
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    "manifest snapshot_count does not match retained snapshots",
                )
            )

    def _validate_result_summary(
        self,
        run_dir: Path,
        summary: dict[str, Any],
        *,
        seen_eval_ids: set[str],
    ) -> str:
        required_fields = {
            "artifact_version",
            "run_id",
            "eval_id",
            "stage",
            "status",
            "created_at",
            "source_path",
            "source_sha256",
            "snapshot_relpath",
            "selection",
            "gate",
            "derived_analysis",
        }
        missing = sorted(field for field in required_fields if field not in summary)
        if missing:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    "results.jsonl entry missing required fields: "
                    + ", ".join(missing),
                )
            )
        if summary["artifact_version"] != RUN_RESULT_VERSION:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    "results.jsonl entry has unsupported artifact_version "
                    f"{summary['artifact_version']!r}",
                )
            )
        if summary["run_id"] != run_dir.name:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"results.jsonl entry has mismatched run_id {summary['run_id']!r}",
                )
            )
        eval_id = summary["eval_id"]
        if not isinstance(eval_id, str) or not eval_id:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    "results.jsonl contains an entry without a non-empty string eval_id",
                )
            )
        if eval_id in seen_eval_ids:
            raise HillClimbHarnessError(
                self._corrupted_run_message(run_dir, f"duplicate eval_id detected: {eval_id}")
            )
        stage = summary["stage"]
        if stage not in HILL_CLIMB_STAGES:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"results.jsonl entry {eval_id} has unknown stage {stage!r}",
                )
            )
        if not eval_id.startswith(f"{stage}_"):
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"results.jsonl entry {eval_id} does not match stage {stage!r}",
                )
            )
        status = summary["status"]
        if status not in RUN_STATUSES:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"results.jsonl entry {eval_id} has unknown status {status!r}",
                )
            )
        for field in ("created_at", "source_path"):
            value = summary[field]
            if not isinstance(value, str) or not value:
                raise HillClimbHarnessError(
                    self._corrupted_run_message(
                        run_dir,
                        f"results.jsonl entry {eval_id} has invalid {field!r}",
                    )
                )
        source_sha256 = summary["source_sha256"]
        if not isinstance(source_sha256, str) or not SHA256_HEX_RE.fullmatch(source_sha256):
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"results.jsonl entry {eval_id} has invalid source_sha256",
                )
            )
        snapshot_relpath = summary["snapshot_relpath"]
        expected_snapshot_relpath = _snapshot_relpath(source_sha256)
        if snapshot_relpath != expected_snapshot_relpath:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"results.jsonl entry {eval_id} must point to {expected_snapshot_relpath!r}, "
                    f"found {snapshot_relpath!r}",
                )
            )
        snapshot_path = run_dir / snapshot_relpath
        if not snapshot_path.exists():
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"missing snapshot referenced by {eval_id}: {snapshot_relpath}",
                )
            )
        for field in ("selection", "gate", "derived_analysis"):
            if not isinstance(summary.get(field), dict):
                raise HillClimbHarnessError(
                    self._corrupted_run_message(
                        run_dir,
                        f"results.jsonl entry {eval_id} has invalid {field!r}",
                    )
                )
        incumbent_before_eval_id = summary.get("incumbent_before_eval_id")
        if incumbent_before_eval_id is not None and (
            not isinstance(incumbent_before_eval_id, str)
            or incumbent_before_eval_id not in seen_eval_ids
        ):
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"results.jsonl entry {eval_id} references unknown incumbent_before_eval_id "
                    f"{incumbent_before_eval_id!r}",
                )
            )
        if status == "invalid":
            error = summary.get("error")
            if not isinstance(error, str) or not error:
                raise HillClimbHarnessError(
                    self._corrupted_run_message(
                        run_dir,
                        f"invalid results.jsonl entry {eval_id} is missing its error message",
                    )
                )
        else:
            if _safe_float(summary.get("mean_edge")) is None:
                raise HillClimbHarnessError(
                    self._corrupted_run_message(
                        run_dir,
                        f"results.jsonl entry {eval_id} is missing a finite mean_edge",
                    )
                )
            if not isinstance(summary.get("scorecard"), dict):
                raise HillClimbHarnessError(
                    self._corrupted_run_message(
                        run_dir,
                        f"results.jsonl entry {eval_id} is missing its scorecard",
                    )
                )
        return eval_id

    def _next_evaluation_id(self, results: list[dict[str, Any]], *, stage: str) -> str:
        return f"{stage}_{len(results) + 1:04d}"

    def _write_snapshot_file(self, snapshot_path: Path, source_text: str) -> None:
        if not snapshot_path.exists():
            snapshot_path.write_text(source_text)

    def _store_snapshot(self, run_dir: Path, source_text: str, source_sha256: str) -> Path:
        snapshot_path = self._snapshot_path(run_dir, source_sha256)
        self._write_snapshot_file(snapshot_path, source_text)
        return snapshot_path

    def _expected_incumbent(
        self, results: list[dict[str, Any]], *, stage: str
    ) -> dict[str, Any] | None:
        for summary in reversed(results):
            if summary.get("stage") == stage and summary.get("status") in {"seed", "keep"}:
                return summary
        return None

    def _read_incumbent(
        self,
        run_dir: Path,
        stage: str,
        results: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        del run_dir
        return self._expected_incumbent(results, stage=stage)

    def _read_latest(
        self, results: list[dict[str, Any]], *, stage: str | None = None
    ) -> dict[str, Any] | None:
        if stage is None:
            return results[-1] if results else None
        for summary in reversed(results):
            if summary.get("stage") == stage:
                return summary
        return None

    def _best_stage_raw(
        self, results: list[dict[str, Any]], *, stage: str
    ) -> dict[str, Any] | None:
        valid = [
            summary
            for summary in results
            if summary.get("stage") == stage
            and _safe_float(summary.get("mean_edge")) is not None
        ]
        if not valid:
            return None
        return max(valid, key=lambda summary: float(summary["mean_edge"]))

    def _evaluation_summary_base(
        self,
        *,
        run_id: str,
        eval_id: str,
        stage: str,
        source_path: Path,
        source_sha256: str,
        label: str | None,
        description: str | None,
        replay_reason: str | None,
        created_at: str,
        incumbent_before: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "artifact_version": RUN_RESULT_VERSION,
            "run_id": run_id,
            "eval_id": eval_id,
            "stage": stage,
            "created_at": created_at,
            "source_path": source_path.as_posix(),
            "source_sha256": source_sha256,
            "snapshot_relpath": _snapshot_relpath(source_sha256),
            "label": label,
            "description": description,
            "replay_reason": replay_reason,
            "incumbent_before_eval_id": None
            if incumbent_before is None
            else incumbent_before.get("eval_id"),
            "incumbent_before_mean_edge": None
            if incumbent_before is None
            else incumbent_before.get("mean_edge"),
        }

    def _reject_duplicate_stage_source(
        self,
        *,
        results: list[dict[str, Any]],
        stage: str,
        source_sha256: str,
        replay_reason: str | None,
    ) -> None:
        if replay_reason is not None:
            return
        for summary in results:
            if summary.get("stage") != stage:
                continue
            if summary.get("source_sha256") == source_sha256:
                raise HillClimbHarnessError(
                    f"Stage {stage!r} already evaluated source {source_sha256}; "
                    "use --replay-reason for an intentional replay."
                )

    def _append_result(self, run_dir: Path, summary: dict[str, Any]) -> None:
        with self._results_path(run_dir).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(summary, sort_keys=True) + "\n")

    def _sync_derived_views(
        self,
        *,
        run_dir: Path,
        manifest: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> None:
        manifest = dict(manifest)
        manifest["updated_at"] = _utc_now()
        latest = results[-1] if results else None
        manifest["latest_eval_id"] = None if latest is None else latest["eval_id"]
        manifest["latest_stage"] = None if latest is None else latest["stage"]
        manifest["eval_count"] = len(results)
        manifest["snapshot_count"] = len({summary["source_sha256"] for summary in results})
        self._manifest_path(run_dir).write_text(_json_dump(manifest))
        self._write_cross_run_index()

    def _build_history(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        history: list[dict[str, Any]] = []
        for summary in results:
            derived = summary.get("derived_analysis", {})
            failure = (
                derived.get("failure_signature", {}) if isinstance(derived, dict) else {}
            )
            history.append(
                {
                    "artifact_version": RUN_HISTORY_VERSION,
                    "eval_id": summary["eval_id"],
                    "stage": summary["stage"],
                    "status": summary["status"],
                    "mean_edge": summary.get("mean_edge"),
                    "delta_vs_incumbent": summary.get("delta_vs_incumbent"),
                    "label": summary.get("label"),
                    "description": summary.get("description"),
                    "strategy_name": summary.get("strategy_name"),
                    "created_at": summary.get("created_at"),
                    "snapshot_relpath": summary.get("snapshot_relpath"),
                    "source_sha256": summary.get("source_sha256"),
                    "incumbent_before_eval_id": summary.get("incumbent_before_eval_id"),
                    "primary_failure_tag": failure.get("primary_tag"),
                    "failure_tags": list(failure.get("tags", [])),
                }
            )
        return history

    def _write_cross_run_index(self) -> dict[str, Any]:
        self.artifact_root.mkdir(parents=True, exist_ok=True)
        entries: list[dict[str, Any]] = []
        valid_indexes: list[int] = []
        for run_dir in sorted(path for path in self.artifact_root.iterdir() if path.is_dir()):
            warnings: list[str] = []
            try:
                manifest = self._load_manifest(
                    run_dir,
                    run_id=run_dir.name,
                    allow_protected_surface_drift=True,
                    warnings=warnings,
                )
                results = self._read_results(run_dir, manifest=manifest)
                latest = results[-1] if results else None
                best_by_stage = {
                    stage: self._index_stage_summary(best)
                    for stage in HILL_CLIMB_STAGES
                    if (best := self._best_stage_raw(results, stage=stage)) is not None
                }
                status = "historical"
                notes = list(warnings)
                if warnings:
                    status = "blocked"
                entry = {
                    "run_id": manifest["run_id"],
                    "status": status,
                    "created_at": manifest["created_at"],
                    "updated_at": manifest["updated_at"],
                    "artifact_dir": run_dir.as_posix(),
                    "eval_count": manifest["eval_count"],
                    "snapshot_count": manifest["snapshot_count"],
                    "latest_eval_id": None if latest is None else latest["eval_id"],
                    "latest_stage": None if latest is None else latest["stage"],
                    "latest_status": None if latest is None else latest["status"],
                    "best_by_stage": best_by_stage,
                    "notes": notes,
                }
                if status != "blocked":
                    valid_indexes.append(len(entries))
                entries.append(entry)
            except Exception as exc:
                entries.append(
                    {
                        "run_id": run_dir.name,
                        "status": "blocked",
                        "created_at": None,
                        "updated_at": None,
                        "artifact_dir": run_dir.as_posix(),
                        "eval_count": None,
                        "snapshot_count": None,
                        "latest_eval_id": None,
                        "latest_stage": None,
                        "latest_status": None,
                        "best_by_stage": {},
                        "notes": [str(exc)],
                    }
                )

        if valid_indexes:
            newest_index = max(
                valid_indexes,
                key=lambda index: (
                    entries[index].get("updated_at") or "",
                    entries[index].get("created_at") or "",
                    entries[index]["run_id"],
                ),
            )
            entries[newest_index]["status"] = "active"

        payload = {
            "artifact_version": CROSS_RUN_INDEX_VERSION,
            "generated_at": _utc_now(),
            "runs": sorted(
                entries,
                key=lambda entry: (
                    entry.get("updated_at") or "",
                    entry.get("created_at") or "",
                    entry["run_id"],
                ),
                reverse=True,
            ),
        }
        (self.artifact_root / "index.json").write_text(_json_dump(payload))
        return payload

    def _index_stage_summary(self, summary: dict[str, Any]) -> dict[str, Any]:
        derived = summary.get("derived_analysis", {})
        failure = (
            derived.get("failure_signature", {}) if isinstance(derived, dict) else {}
        )
        return {
            "eval_id": summary["eval_id"],
            "status": summary["status"],
            "mean_edge": summary.get("mean_edge"),
            "label": summary.get("label"),
            "strategy_name": summary.get("strategy_name"),
            "failure_tags": list(failure.get("tags", [])),
        }

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

    def _build_gate(self, *, scorecard: dict[str, Any], stage_config: Any) -> dict[str, Any]:
        thresholds: dict[str, float] = {}
        failures: list[str] = []
        overall = scorecard.get("overall", {})
        mean_edge = _safe_float(overall.get("mean_edge"))
        if stage_config.min_mean_edge is not None:
            thresholds["mean_edge"] = float(stage_config.min_mean_edge)
            if mean_edge is None:
                failures.append("mean_edge is required for this stage")
            elif mean_edge < float(stage_config.min_mean_edge):
                failures.append(
                    f"mean_edge={mean_edge:.6f} is below stage threshold "
                    f"{float(stage_config.min_mean_edge):.6f}"
                )
        arb_loss_ratio = _safe_float(overall.get("arb_loss_to_retail_gain"))
        if getattr(stage_config, "max_arb_loss_to_retail_gain", None) is not None:
            thresholds["arb_loss_to_retail_gain"] = float(
                stage_config.max_arb_loss_to_retail_gain
            )
            if arb_loss_ratio is None:
                failures.append("arb_loss_to_retail_gain is required for this stage")
            elif arb_loss_ratio > float(stage_config.max_arb_loss_to_retail_gain):
                failures.append(
                    "arb_loss_to_retail_gain="
                    f"{arb_loss_ratio:.6f} exceeds stage threshold "
                    f"{float(stage_config.max_arb_loss_to_retail_gain):.6f}"
                )
        max_fee_jump = _safe_float(overall.get("max_fee_jump"))
        if getattr(stage_config, "max_fee_jump", None) is not None:
            thresholds["max_fee_jump"] = float(stage_config.max_fee_jump)
            if max_fee_jump is None:
                failures.append("max_fee_jump is required for this stage")
            elif max_fee_jump > float(stage_config.max_fee_jump):
                failures.append(
                    f"max_fee_jump={max_fee_jump:.6f} exceeds stage threshold "
                    f"{float(stage_config.max_fee_jump):.6f}"
                )
        return {
            "stage": stage_config.name,
            "thresholds": thresholds,
            "required_metric_fields": sorted(thresholds),
            "passed": not failures,
            "failures": failures,
        }

    def _slice_metric(
        self,
        scorecard: dict[str, Any],
        *,
        collection: str,
        bucket: str,
        metric: str = "mean_edge",
    ) -> float | None:
        by_slice = scorecard.get("by_slice", {})
        group = by_slice.get(collection, {}) if isinstance(by_slice, dict) else {}
        bucket_payload = group.get(bucket, {}) if isinstance(group, dict) else {}
        if not isinstance(bucket_payload, dict):
            return None
        return _safe_float(bucket_payload.get(metric))

    def _extract_profile(self, scorecard: dict[str, Any]) -> dict[str, float | None]:
        overall = scorecard.get("overall", {})
        if not isinstance(overall, dict):
            overall = {}
        profile = {field: _safe_float(overall.get(field)) for field in PROFILE_FIELDS}
        profile.update(
            {
                "low_decile_mean_edge": self._slice_metric(
                    scorecard,
                    collection="mean_edge_deciles",
                    bucket="d01",
                ),
                "median_decile_mean_edge": self._slice_metric(
                    scorecard,
                    collection="mean_edge_deciles",
                    bucket="d05",
                ),
                "high_decile_mean_edge": self._slice_metric(
                    scorecard,
                    collection="mean_edge_deciles",
                    bucket="d10",
                ),
                "low_retail_mean_edge": self._slice_metric(
                    scorecard,
                    collection="retail_intensity_terciles",
                    bucket="low",
                ),
                "low_volatility_mean_edge": self._slice_metric(
                    scorecard,
                    collection="volatility_terciles",
                    bucket="low",
                ),
            }
        )
        return profile

    def _compare_profile_maps(
        self,
        current: dict[str, float | None],
        baseline: dict[str, float | None],
    ) -> dict[str, float | None]:
        return {
            key: _delta(current.get(key), baseline.get(key))
            for key in sorted(set(current) | set(baseline))
        }

    def _build_failure_signature(
        self,
        *,
        deltas: dict[str, float | None],
        overall_delta: float | None,
    ) -> dict[str, Any]:
        tags: list[str] = []
        notes: list[str] = []
        arb_edge_delta = deltas.get("arb_edge")
        arb_loss_ratio_delta = deltas.get("arb_loss_to_retail_gain")
        if (arb_edge_delta is not None and arb_edge_delta < -10.0) or (
            arb_loss_ratio_delta is not None and arb_loss_ratio_delta > 0.03
        ):
            tags.append("over_open_leak")
            notes.append("candidate reopened too much safe-side flow and worsened arb leakage")
        low_slice_delta = deltas.get("low_retail_mean_edge")
        low_volatility_delta = deltas.get("low_volatility_mean_edge")
        low_decile_delta = deltas.get("low_decile_mean_edge")
        mean_fee_delta = deltas.get("time_weighted_mean_fee")
        if (
            (
                low_slice_delta is not None
                and low_slice_delta < -5.0
            )
            or (
                low_volatility_delta is not None
                and low_volatility_delta < -5.0
            )
            or (
                low_decile_delta is not None
                and low_decile_delta < -10.0
            )
        ) and (
            mean_fee_delta is not None
            and mean_fee_delta > 0.0005
        ):
            tags.append("over_tighten_clamp")
            notes.append("calm or protected floor slices regressed while average fees tightened")
        high_decile_delta = deltas.get("high_decile_mean_edge")
        if (
            low_decile_delta is not None
            and low_decile_delta < -10.0
            and high_decile_delta is not None
            and high_decile_delta <= 0.0
        ):
            tags.append("crossover_regression")
            notes.append(
                "cross-interface change regressed the protected floor without compensating upside"
            )
        meaningful_outcome_motion = any(
            (delta := deltas.get(metric)) is not None and abs(delta) > threshold
            for metric, threshold in (
                ("arb_loss_to_retail_gain", 0.02),
                ("quote_selectivity_ratio", 3.0),
                ("time_weighted_mean_fee", 0.001),
                ("low_retail_mean_edge", 5.0),
                ("low_volatility_mean_edge", 5.0),
                ("low_decile_mean_edge", 7.5),
            )
        )
        if overall_delta is not None and overall_delta <= 0.0:
            if any(
                (delta := deltas.get(field)) is not None and delta > 0.0
                for field in ("low_retail_mean_edge", "low_volatility_mean_edge")
            ):
                tags.append("crossover_regression")
                notes.append(
                    "some slices improved, but the crossover regressed elsewhere and failed overall"
                )
            elif not meaningful_outcome_motion:
                tags.append("frontier_neighbor")
                notes.append(
                    "candidate stayed too close to the incumbent outcome basin to improve overall edge"
                )
        ordered_tags = []
        for candidate in (
            "crossover_regression",
            "over_open_leak",
            "over_tighten_clamp",
            "frontier_neighbor",
        ):
            if candidate in tags:
                ordered_tags.append(candidate)
        primary_tag = ordered_tags[0] if ordered_tags else None
        if primary_tag is None and overall_delta is not None and overall_delta > 0.0:
            primary_tag = "improving_variant"
        return {
            "tags": ordered_tags,
            "primary_tag": primary_tag,
            "notes": notes,
        }

    def _build_derived_analysis(
        self,
        *,
        scorecard: dict[str, Any],
        incumbent_before: dict[str, Any] | None,
    ) -> dict[str, Any]:
        profile = self._extract_profile(scorecard)
        incumbent_profile = None
        deltas: dict[str, float | None] = {}
        if incumbent_before is not None:
            incumbent_scorecard = incumbent_before.get("scorecard", {})
            if isinstance(incumbent_scorecard, dict):
                incumbent_profile = self._extract_profile(incumbent_scorecard)
                deltas = self._compare_profile_maps(profile, incumbent_profile)
        overall_delta = deltas.get("mean_edge")
        return {
            "profile": profile,
            "incumbent_profile": incumbent_profile,
            "delta_vs_incumbent_profile": deltas,
            "failure_signature": self._build_failure_signature(
                deltas=deltas,
                overall_delta=overall_delta,
            ),
        }

    def _build_invalid_analysis(self, error: str) -> dict[str, Any]:
        return {
            "profile": {},
            "incumbent_profile": None,
            "delta_vs_incumbent_profile": {},
            "failure_signature": {
                "tags": ["invalid_eval"],
                "primary_tag": "invalid_eval",
                "notes": [error],
            },
        }

    def _resolve_profile_input(
        self,
        *,
        stage: str,
        summary: dict[str, Any] | None = None,
        source_path: Path | str | None = None,
    ) -> dict[str, Any]:
        if (summary is None) == (source_path is None):
            raise HillClimbHarnessError(
                "Provide exactly one of a stored eval summary or a source path"
            )
        stage_name = resolve_hill_climb_stage(stage).name
        if summary is not None:
            if summary.get("stage") != stage_name:
                raise HillClimbHarnessError(
                    f"Stored eval {summary.get('eval_id')!r} belongs to stage {summary.get('stage')!r}, not {stage_name!r}"
                )
            scorecard = summary.get("scorecard")
            if not isinstance(scorecard, dict):
                raise HillClimbHarnessError(
                    f"Stored eval {summary.get('eval_id')!r} is missing a scorecard"
                )
            return {
                "kind": "stored_eval",
                "eval_id": summary.get("eval_id"),
                "mean_edge": summary.get("mean_edge"),
                "profile": self._extract_profile(scorecard),
            }
        assert source_path is not None
        source = Path(source_path)
        if not source.exists():
            raise HillClimbHarnessError(f"Strategy file not found: {source}")
        source_profile = self.profile_source(stage=stage_name, source_path=source)
        return {
            "kind": "source",
            "eval_id": None,
            "source_path": source.as_posix(),
            "mean_edge": source_profile["mean_edge"],
            "profile": source_profile["profile"],
        }

    def profile_source(self, *, stage: str, source_path: Path | str) -> dict[str, Any]:
        """Evaluate a source ad hoc and return only its profile payload."""
        self._protected_surface().ensure_runtime_eval_allowed()
        stage_config = resolve_hill_climb_stage(stage)
        source = Path(source_path)
        source_text = self._read_source(source)
        _strategy, scorecard, _gate = self._run_stage_evaluation(
            stage_config=stage_config,
            source_text=source_text,
        )
        return {
            "mean_edge": float(scorecard["overall"]["mean_edge"]),
            "scorecard": scorecard,
            "profile": self._extract_profile(scorecard),
        }

    def probe_source(self, *, stage: str, source_path: Path | str) -> dict[str, Any]:
        """Evaluate a source without creating retained artifacts."""
        self._protected_surface().ensure_runtime_eval_allowed()
        stage_config = resolve_hill_climb_stage(stage)
        source = Path(source_path)
        if not source.exists():
            raise HillClimbHarnessError(f"Strategy file not found: {source}")
        source_text = self._read_source(source)
        source_sha256 = _sha256(source_text)
        try:
            strategy, scorecard, gate = self._run_stage_evaluation(
                stage_config=stage_config,
                source_text=source_text,
            )
        except Exception as exc:
            raise HillClimbHarnessError(f"Probe failed for {source}: {exc}") from exc
        return {
            "mode": "probe",
            "stage": stage_config.name,
            "source_path": source.as_posix(),
            "source_sha256": source_sha256,
            "strategy_name": strategy.get_name(),
            "mean_edge": float(scorecard["overall"]["mean_edge"]),
            "gate": gate,
            "selection": {
                "promotion_margin": None,
                "rationale": "probe only; not recorded in the retained lane",
            },
            "scorecard": scorecard,
            "derived_analysis": self._build_derived_analysis(
                scorecard=scorecard,
                incumbent_before=None,
            ),
        }

    def _run_stage_evaluation(
        self,
        *,
        stage_config: Any,
        source_text: str,
    ) -> tuple[EVMStrategyAdapter, dict[str, Any], dict[str, Any]]:
        strategy = self._strategy_loader(source_text)
        result = self._stage_runner_factory(stage_config.name, self.n_workers).run_match(
            strategy,
            self._baseline_loader(),
            store_results=True,
        )
        scorecard = compute_scorecard(result)
        scorecard["run_metadata"]["stage"] = stage_config.name
        scorecard["run_metadata"]["seed_block"] = list(stage_config.seed_block)
        gate = self._build_gate(scorecard=scorecard, stage_config=stage_config)
        return strategy, scorecard, gate

    def _corrupted_run_message(self, run_dir: Path, problem: str) -> str:
        return (
            f"Run '{run_dir.name}' is corrupted: {problem}. "
            "Retained lanes may only keep run.json, results.jsonl, and referenced snapshots; "
            "worker-local exploration should use hill-climb probe and only selected branches "
            "should be rerun into a canonical run_id."
        )

    def _assert_retained_run_id_allowed(self, run_id: str) -> None:
        if WORKER_RUN_ID_RE.search(run_id):
            raise HillClimbHarnessError(
                f"Worker-style run_id {run_id!r} is scratch-only and cannot live under "
                f"{self.artifact_root}. Use `amm-match hill-climb probe --stage ...` in the "
                "worktree, then rerun only the chosen branch into the canonical retained run."
            )

    def _protected_surface(self) -> Any:
        if self._protected_surface_checker is None:
            self._protected_surface_checker = ProtectedSurfaceChecker.discover()
        return self._protected_surface_checker
