"""Append-only hill-climb harness for agent-driven strategy iteration."""

from __future__ import annotations

from collections.abc import Mapping
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

ARTIFACT_VERSION = "hill_climb.v3"
RUN_MANIFEST_VERSION = "hill_climb.run.v4"
RUN_STATE_VERSION = "hill_climb.state.v2"
SNAPSHOT_LAYOUT_VERSION = "flat_snapshots.v1"
HISTORY_VERSION = "hill_climb.history.v1"
HYPOTHESIS_VERSION = "hill_climb.hypothesis.v1"
CROSS_RUN_INDEX_VERSION = "hill_climb.index.v1"
ANALYSIS_VERSION = "hill_climb.analysis.v1"
INCUMBENT_EPSILON = 1e-9
NEXT_EVAL_INDEX_FILENAME = ".next_eval_index"
LEGACY_NEXT_EVAL_ID_FILENAME = ".next_eval_id"
LEGACY_BATCH_KEY = "__legacy__"
SAME_SPINE_FAILURE_LOOKBACK = 12
DECOMPOSITION_LAYERS = (
    "state",
    "risk_budget",
    "opportunity_budget",
    "quote_map",
)
OPEN_HYPOTHESIS_STATUSES = {"planned", "queued", "active"}
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
HYPOTHESIS_STATUSES = {
    "planned",
    "queued",
    "active",
    "promoted",
    "invalidated",
    "abandoned",
    "completed",
    "seed",
    "keep",
    "discard",
    "invalid",
}
PROFILE_FIELDS = (
    "mean_edge",
    "retail_edge",
    "arb_edge",
    "arb_loss_to_retail_gain",
    "time_weighted_bid_fee",
    "time_weighted_ask_fee",
    "max_fee_jump",
)
SLICE_PROFILE_FIELDS = (
    "low_decile_mean_edge",
    "median_decile_mean_edge",
    "high_decile_mean_edge",
    "low_retail_mean_edge",
    "low_volatility_mean_edge",
)
EXPERIMENT_METRIC_FIELDS = PROFILE_FIELDS + SLICE_PROFILE_FIELDS
FAILURE_TAGS = {
    "arb_leak_regression",
    "overpriced_calm_flow",
    "over_spiky_fee_surface",
    "tail_protection_loss",
    "weak_slice_improvement_without_overall_gain",
}
VALID_FAILURE_MODES = FAILURE_TAGS | {"invalid_eval", "improving_variant"}
PLANNING_INTENTS = (
    "local_refine",
    "anti_arb",
    "weak_slice",
    "fee_discipline",
    "structural_pivot",
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


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def _json_search_blob(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).lower()


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
class OutcomeGateStatus:
    """Explicit user-visible success gate for thresholded optimization tasks."""

    stage: str
    minimum_mean_edge: float
    incumbent_mean_edge: float | None
    passed: bool
    message: str


@dataclass(frozen=True)
class RunStateStatus:
    """Validated persisted loop state plus derived operator guidance."""

    run_id: str
    baseline_eval_id: str | None
    current_target_stage: str
    incumbent_eval_ids: dict[str, str]
    last_completed_iteration: int
    next_hypothesis_id: str | None
    next_hypothesis_note: str | None
    run_mode: str
    stop_rules: dict[str, int]
    updated_at: str
    outcome_gate: OutcomeGateStatus | None
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


def _ensure_text_file(path: Path, contents: str) -> None:
    if not path.exists():
        path.write_text(contents)


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
        hypothesis_id: str | None = None,
        parent_eval_id: str | None = None,
        change_summary: str | None = None,
        research_refs: list[str] | None = None,
        replay_reason: str | None = None,
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
        lineage = self._resolve_lineage(
            run_dir,
            hypothesis_id=hypothesis_id,
            parent_eval_id=parent_eval_id,
            stage=stage_config.name,
            source_sha256=source_sha256,
            replay_reason=replay_reason,
        )
        try:
            eval_id = self._reserve_evaluation_id(
                run_dir=run_dir, stage=stage_config.name
            )
        except Exception:
            with self._run_lock(run_dir):
                self._release_pending_source(
                    run_dir,
                    stage=stage_config.name,
                    source_sha256=source_sha256,
                )
            raise
        normalized_research_refs = self._normalize_string_list(research_refs)
        summary_base = self._evaluation_summary_base(
            run_id=normalized_run_id,
            eval_id=eval_id,
            stage_config=stage_config,
            source_path=source_path,
            source_sha256=source_sha256,
            snapshot_path=snapshot_path,
            label=label,
            description=description,
            lineage=lineage,
            change_summary=change_summary,
            research_refs=normalized_research_refs,
            replay_reason=replay_reason,
        )

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
                scorecard=scorecard,
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
                **summary_base,
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
                "incumbent_before": self._read_incumbent(run_dir, stage_config.name),
                "error": str(exc),
                "derived_analysis": self._build_invalid_analysis(str(exc)),
            }
            with self._run_lock(run_dir):
                try:
                    self._append_result(run_dir, summary)
                    self._link_hypothesis_eval(run_dir, summary)
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
                    self._sync_derived_views(run_dir)
                finally:
                    self._release_pending_source(
                        run_dir,
                        stage=stage_config.name,
                        source_sha256=source_sha256,
                    )
            raise HillClimbHarnessError(
                f"Evaluation failed for {source_path}: {exc}"
            ) from exc

        with self._run_lock(run_dir):
            try:
                self._append_result(run_dir, summary)
                self._link_hypothesis_eval(run_dir, summary)
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
                self._sync_derived_views(run_dir)
            finally:
                self._release_pending_source(
                    run_dir,
                    stage=stage_config.name,
                    source_sha256=source_sha256,
                )
        return summary

    def get_stage_status(
        self,
        *,
        run_id: str,
        stage: str,
        allow_protected_surface_drift: bool = False,
    ) -> StageStatus:
        """Return the latest and incumbent summaries for a run stage."""
        normalized_run_id = _slug(run_id, fallback="run")
        stage_config = resolve_hill_climb_stage(stage)
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        self._validate_current_run(
            run_dir,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        latest = self._read_latest(run_dir, stage_config.name)
        incumbent = self._read_incumbent(run_dir, stage_config.name)
        return StageStatus(
            run_id=normalized_run_id,
            stage=stage_config.name,
            incumbent=incumbent,
            latest=latest,
        )

    def get_run_state(
        self,
        *,
        run_id: str,
        allow_protected_surface_drift: bool = False,
    ) -> RunStateStatus:
        """Return validated loop state and derived stop-rule guidance."""
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        self._validate_current_run(
            run_dir,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        results = self._read_results(run_dir)
        state = self._load_state_payload(run_dir, require_current=True)
        return self._run_state_status_from_payload(state, results)

    def update_run_state(
        self,
        *,
        run_id: str,
        current_target_stage: str | None = None,
        next_hypothesis_id: str | None = None,
        next_hypothesis_id_set: bool = False,
        next_hypothesis_note: str | None = None,
        next_hypothesis_note_set: bool = False,
        run_mode: str | None = None,
        stop_rules: dict[str, int] | None = None,
        outcome_gate: dict[str, Any] | None = None,
        outcome_gate_set: bool = False,
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
            if next_hypothesis_id_set:
                updated_state["next_hypothesis_id"] = next_hypothesis_id
                if next_hypothesis_id is None:
                    updated_state["next_hypothesis_note"] = None
            if next_hypothesis_note_set:
                updated_state["next_hypothesis_note"] = next_hypothesis_note
            if run_mode is not None:
                updated_state["run_mode"] = run_mode
            if stop_rules is not None:
                updated_state["stop_rules"] = stop_rules
            if outcome_gate_set:
                updated_state["outcome_gate"] = outcome_gate
            updated_state["updated_at"] = _utc_now()
            self._validate_state(run_dir, updated_state, results)
            self._write_state(run_dir, updated_state)
            self._sync_derived_views(run_dir)
        return self._run_state_status_from_payload(updated_state, results)

    def upsert_hypothesis(
        self,
        *,
        run_id: str,
        hypothesis_id: str,
        title: str | None = None,
        rationale: str | None = None,
        expected_effect: str | None = None,
        mutation_family: str | None = None,
        status: str | None = None,
        batch_id: str | None = None,
        parent_hypothesis_id: str | None = None,
        seed_eval_id: str | None = None,
        research_refs: list[str] | None = None,
        target_metrics: dict[str, float] | None = None,
        hard_guardrails: dict[str, float] | None = None,
        expected_failure_mode: str | None = None,
        actual_failure_mode: str | None = None,
        novelty_coordinates: dict[str, Any] | None = None,
        synthesis_eligible: bool | None = None,
        nearest_prior_failures: list[str] | None = None,
        nearest_prior_successes: list[str] | None = None,
        primary_layer_changed: str | None = None,
        layer_held_fixed: str | None = None,
        hidden_coupling_removed: str | None = None,
        why_not_coefficient_retune: str | None = None,
        expected_win_condition: str | None = None,
        expected_failure_signature: str | None = None,
        quote_topology: str | None = None,
        is_topology_branch: bool | None = None,
    ) -> dict[str, Any]:
        """Create or update a hypothesis record for a run."""
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")

        with self._run_lock(run_dir):
            self._validate_current_run(run_dir)
            hypotheses = self._load_hypotheses(run_dir)
            payload = hypotheses.get(hypothesis_id)
            created_at = _utc_now()
            if payload is None:
                missing = [
                    name
                    for name, value in (
                        ("title", title),
                        ("rationale", rationale),
                        ("expected_effect", expected_effect),
                        ("mutation_family", mutation_family),
                        ("batch_id", batch_id),
                        ("primary_layer_changed", primary_layer_changed),
                        ("layer_held_fixed", layer_held_fixed),
                        ("hidden_coupling_removed", hidden_coupling_removed),
                        ("why_not_coefficient_retune", why_not_coefficient_retune),
                        ("expected_win_condition", expected_win_condition),
                        ("expected_failure_signature", expected_failure_signature),
                        ("quote_topology", quote_topology),
                        ("is_topology_branch", is_topology_branch),
                    )
                    if value is None
                ]
                if missing:
                    raise HillClimbHarnessError(
                        "New hypotheses require " + ", ".join(missing)
                    )
                payload = {
                    "artifact_version": HYPOTHESIS_VERSION,
                    "hypothesis_id": hypothesis_id,
                    "title": title,
                    "rationale": rationale,
                    "expected_effect": expected_effect,
                    "mutation_family": mutation_family,
                    "status": status or "queued",
                    "batch_id": self._normalize_optional_text(
                        batch_id,
                        field_name="batch_id",
                    ),
                    "created_at": created_at,
                    "updated_at": created_at,
                    "parent_hypothesis_id": parent_hypothesis_id,
                    "seed_eval_id": seed_eval_id,
                    "eval_ids": [],
                    "research_refs": self._normalize_string_list(research_refs),
                    "target_metrics": self._normalize_float_mapping(
                        target_metrics,
                        field_name="target_metrics",
                    ),
                    "hard_guardrails": self._normalize_float_mapping(
                        hard_guardrails,
                        field_name="hard_guardrails",
                    ),
                    "expected_failure_mode": expected_failure_mode,
                    "actual_failure_mode": actual_failure_mode,
                    "novelty_coordinates": self._normalize_json_object(
                        novelty_coordinates
                    ),
                    "synthesis_eligible": True
                    if synthesis_eligible is None
                    else synthesis_eligible,
                    "nearest_prior_failures": self._normalize_string_list(
                        nearest_prior_failures
                    ),
                    "nearest_prior_successes": self._normalize_string_list(
                        nearest_prior_successes
                    ),
                    "primary_layer_changed": self._normalize_decomposition_layer(
                        primary_layer_changed,
                        field_name="primary_layer_changed",
                    ),
                    "layer_held_fixed": self._normalize_decomposition_layer(
                        layer_held_fixed,
                        field_name="layer_held_fixed",
                    ),
                    "hidden_coupling_removed": self._normalize_optional_text(
                        hidden_coupling_removed,
                        field_name="hidden_coupling_removed",
                    ),
                    "why_not_coefficient_retune": self._normalize_optional_text(
                        why_not_coefficient_retune,
                        field_name="why_not_coefficient_retune",
                    ),
                    "expected_win_condition": self._normalize_optional_text(
                        expected_win_condition,
                        field_name="expected_win_condition",
                    ),
                    "expected_failure_signature": self._normalize_optional_text(
                        expected_failure_signature,
                        field_name="expected_failure_signature",
                    ),
                    "quote_topology": self._normalize_optional_text(
                        quote_topology,
                        field_name="quote_topology",
                    ),
                    "is_topology_branch": is_topology_branch,
                }
            else:
                payload = dict(payload)
                if title is not None:
                    payload["title"] = title
                if rationale is not None:
                    payload["rationale"] = rationale
                if expected_effect is not None:
                    payload["expected_effect"] = expected_effect
                if mutation_family is not None:
                    payload["mutation_family"] = mutation_family
                if status is not None:
                    payload["status"] = status
                if batch_id is not None:
                    payload["batch_id"] = self._normalize_optional_text(
                        batch_id,
                        field_name="batch_id",
                    )
                if parent_hypothesis_id is not None:
                    payload["parent_hypothesis_id"] = parent_hypothesis_id
                if seed_eval_id is not None:
                    payload["seed_eval_id"] = seed_eval_id
                if research_refs is not None:
                    payload["research_refs"] = self._normalize_string_list(
                        research_refs
                    )
                if target_metrics is not None:
                    payload["target_metrics"] = self._normalize_float_mapping(
                        target_metrics,
                        field_name="target_metrics",
                    )
                if hard_guardrails is not None:
                    payload["hard_guardrails"] = self._normalize_float_mapping(
                        hard_guardrails,
                        field_name="hard_guardrails",
                    )
                if expected_failure_mode is not None:
                    payload["expected_failure_mode"] = expected_failure_mode
                if actual_failure_mode is not None:
                    payload["actual_failure_mode"] = actual_failure_mode
                if novelty_coordinates is not None:
                    payload["novelty_coordinates"] = self._normalize_json_object(
                        novelty_coordinates
                    )
                if synthesis_eligible is not None:
                    payload["synthesis_eligible"] = synthesis_eligible
                if nearest_prior_failures is not None:
                    payload["nearest_prior_failures"] = self._normalize_string_list(
                        nearest_prior_failures
                    )
                if nearest_prior_successes is not None:
                    payload["nearest_prior_successes"] = self._normalize_string_list(
                        nearest_prior_successes
                    )
                if primary_layer_changed is not None:
                    payload["primary_layer_changed"] = (
                        self._normalize_decomposition_layer(
                            primary_layer_changed,
                            field_name="primary_layer_changed",
                        )
                    )
                if layer_held_fixed is not None:
                    payload["layer_held_fixed"] = self._normalize_decomposition_layer(
                        layer_held_fixed,
                        field_name="layer_held_fixed",
                    )
                if hidden_coupling_removed is not None:
                    payload["hidden_coupling_removed"] = self._normalize_optional_text(
                        hidden_coupling_removed,
                        field_name="hidden_coupling_removed",
                    )
                if why_not_coefficient_retune is not None:
                    payload["why_not_coefficient_retune"] = (
                        self._normalize_optional_text(
                            why_not_coefficient_retune,
                            field_name="why_not_coefficient_retune",
                        )
                    )
                if expected_win_condition is not None:
                    payload["expected_win_condition"] = self._normalize_optional_text(
                        expected_win_condition,
                        field_name="expected_win_condition",
                    )
                if expected_failure_signature is not None:
                    payload["expected_failure_signature"] = (
                        self._normalize_optional_text(
                            expected_failure_signature,
                            field_name="expected_failure_signature",
                        )
                    )
                if quote_topology is not None:
                    payload["quote_topology"] = self._normalize_optional_text(
                        quote_topology,
                        field_name="quote_topology",
                    )
                if is_topology_branch is not None:
                    payload["is_topology_branch"] = is_topology_branch
                payload["updated_at"] = created_at
            if (
                payload.get("parent_hypothesis_id") is not None
                and payload["parent_hypothesis_id"] not in hypotheses
            ):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has no parent hypothesis {payload['parent_hypothesis_id']!r}"
                )
            self._validate_hypothesis(
                run_dir, payload, results=self._read_results(run_dir)
            )
            self._write_hypothesis(run_dir, payload)
            self._sync_derived_views(run_dir)
        return payload

    def get_history(
        self, *, run_id: str, allow_protected_surface_drift: bool = False
    ) -> list[dict[str, Any]]:
        """Return the compact derived history view for a run."""
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        self._validate_current_run(
            run_dir,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        return self._build_history(self._read_results(run_dir))

    def get_evaluation(
        self,
        *,
        run_id: str,
        eval_id: str,
        allow_protected_surface_drift: bool = False,
    ) -> dict[str, Any]:
        """Return one evaluation summary by id."""
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        self._validate_current_run(
            run_dir,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        for summary in self._read_results(run_dir):
            if summary["eval_id"] == eval_id:
                return summary
        raise HillClimbHarnessError(
            f"Run '{normalized_run_id}' has no evaluation {eval_id!r}"
        )

    def get_hypothesis(
        self,
        *,
        run_id: str,
        hypothesis_id: str,
        allow_protected_surface_drift: bool = False,
    ) -> dict[str, Any]:
        """Return one hypothesis record by id."""
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        self._validate_current_run(
            run_dir,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        payload = self._load_hypotheses(run_dir).get(hypothesis_id)
        if payload is None:
            raise HillClimbHarnessError(
                f"Run '{normalized_run_id}' has no hypothesis {hypothesis_id!r}"
            )
        return payload

    def summarize_run(
        self, *, run_id: str, allow_protected_surface_drift: bool = False
    ) -> dict[str, Any]:
        """Return an agent-facing summary for one run."""
        context = self._read_run_context(
            run_id,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        state = self._run_state_status_from_payload(
            context["state"], context["results"]
        )
        history = self._build_history(context["results"])
        hypotheses = sorted(
            context["hypotheses"].values(),
            key=lambda payload: payload["hypothesis_id"],
        )
        promoted = [entry for entry in history if entry["status"] in {"seed", "keep"}]
        notable_failures = [
            entry for entry in history if entry["status"] in {"discard", "invalid"}
        ]
        unresolved = [
            payload
            for payload in hypotheses
            if payload["status"] in {"planned", "queued", "active"}
        ]
        analysis = self._build_run_analysis(
            run_dir=context["run_dir"],
            results=context["results"],
            hypotheses=context["hypotheses"],
            warnings=context["warnings"],
        )
        return {
            "run_id": state.run_id,
            "current_target_stage": state.current_target_stage,
            "outcome_gate": None
            if state.outcome_gate is None
            else {
                "stage": state.outcome_gate.stage,
                "minimum_mean_edge": state.outcome_gate.minimum_mean_edge,
                "passed": state.outcome_gate.passed,
                "message": state.outcome_gate.message,
            },
            "warnings": context["warnings"],
            "incumbent_chain": promoted,
            "frontier_bank": analysis["frontier_bank"],
            "failure_clusters": analysis["failure_clusters"],
            "intent_coverage": analysis["intent_coverage"],
            "decomposition_coverage": analysis["decomposition_coverage"],
            "decomposition_gaps": analysis["decomposition_gaps"],
            "batch_diversity": analysis["batch_diversity"],
            "structural_recommendations": analysis["structural_recommendations"],
            "portfolio_gaps": analysis["portfolio_gaps"],
            "recommended_next_batch": analysis["recommended_next_batch"],
            "abandoned_families": sorted(
                {
                    payload["mutation_family"]
                    for payload in hypotheses
                    if payload["status"] in {"abandoned", "invalidated"}
                }
            ),
            "unresolved_hypotheses": unresolved,
            "notable_failures": notable_failures[-5:],
        }

    def analyze_run(
        self, *, run_id: str, allow_protected_surface_drift: bool = False
    ) -> dict[str, Any]:
        """Return a structured phenotype and frontier analysis for one run."""
        context = self._read_run_context(
            run_id,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        return self._build_run_analysis(
            run_dir=context["run_dir"],
            results=context["results"],
            hypotheses=context["hypotheses"],
            warnings=context["warnings"],
        )

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
        anchor_profile = (
            None
            if anchor_summary is None and anchor_source_path is None
            else self._resolve_profile_input(
                stage=stage,
                summary=anchor_summary,
                source_path=anchor_source_path,
            )
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
        if anchor_profile is not None:
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

    def _build_run_analysis(
        self,
        *,
        run_dir: Path,
        results: list[dict[str, Any]],
        hypotheses: dict[str, dict[str, Any]],
        warnings: list[str],
    ) -> dict[str, Any]:
        frontier_bank = self._build_frontier_bank(results)
        failure_clusters = self._build_failure_clusters(results)
        active_batch_id, selection_mode, active_open_payloads = (
            self._select_active_open_batch(hypotheses)
        )
        active_open_ids = {
            payload["hypothesis_id"] for payload in active_open_payloads
        }
        if selection_mode == "legacy_open_pool" and len(active_open_payloads) >= 2:
            warnings = [
                *warnings,
                (
                    "Batch diversity is using a legacy open-hypothesis pool because the "
                    "active hypotheses do not declare batch_id. Add batch_id when seeding "
                    "new hypotheses for precise batch-scoped coverage."
                ),
            ]
        phenotype_coverage = {
            payload["hypothesis_id"]: self._hypothesis_analysis_entry(payload)
            for payload in sorted(
                hypotheses.values(), key=lambda payload: payload["hypothesis_id"]
            )
        }
        intent_coverage = self._build_intent_coverage(
            hypotheses,
            active_open_ids=active_open_ids,
        )
        decomposition_coverage = self._build_decomposition_coverage(
            hypotheses,
            active_open_ids=active_open_ids,
        )
        decomposition_gaps = self._decomposition_gaps(decomposition_coverage)
        batch_diversity = self._build_batch_diversity(
            batch_id=active_batch_id,
            selection_mode=selection_mode,
            open_payloads=active_open_payloads,
            results=results,
            hypotheses=hypotheses,
            decomposition_coverage=decomposition_coverage,
        )
        return {
            "artifact_version": ANALYSIS_VERSION,
            "run_id": run_dir.name,
            "warnings": warnings,
            "frontier_bank": frontier_bank,
            "failure_clusters": failure_clusters,
            "recent_failures": [
                summary
                for summary in results
                if summary.get("status") in {"discard", "invalid"}
            ][-5:],
            "phenotype_coverage": phenotype_coverage,
            "intent_coverage": intent_coverage,
            "decomposition_coverage": decomposition_coverage,
            "decomposition_gaps": decomposition_gaps,
            "batch_diversity": batch_diversity,
            "structural_recommendations": self._structural_recommendations(
                decomposition_gaps=decomposition_gaps,
                batch_diversity=batch_diversity,
            ),
            "portfolio_gaps": self._portfolio_gaps(intent_coverage),
            "recommended_next_batch": self._recommended_next_batch(
                frontier_bank=frontier_bank,
                failure_clusters=failure_clusters,
                intent_coverage=intent_coverage,
            ),
        }

    def _build_failure_clusters(self, results: list[dict[str, Any]]) -> dict[str, int]:
        failure_clusters: dict[str, int] = {}
        for summary in results:
            derived = summary.get("derived_analysis", {})
            failure = derived.get("failure_signature", {})
            for tag in failure.get("tags", []):
                failure_clusters[tag] = failure_clusters.get(tag, 0) + 1
        return dict(sorted(failure_clusters.items()))

    def _hypothesis_analysis_entry(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "mutation_family": payload["mutation_family"],
            "batch_id": payload.get("batch_id"),
            "novelty_coordinates": payload.get("novelty_coordinates", {}),
            "target_metrics": payload.get("target_metrics", {}),
            "hard_guardrails": payload.get("hard_guardrails", {}),
            "expected_failure_mode": payload.get("expected_failure_mode"),
            "actual_failure_mode": payload.get("actual_failure_mode"),
            "synthesis_eligible": payload.get("synthesis_eligible", True),
            "intents": self._infer_hypothesis_intents(payload),
            "primary_layer_changed": payload.get("primary_layer_changed"),
            "layer_held_fixed": payload.get("layer_held_fixed"),
            "hidden_coupling_removed": payload.get("hidden_coupling_removed"),
            "why_not_coefficient_retune": payload.get("why_not_coefficient_retune"),
            "expected_win_condition": payload.get("expected_win_condition"),
            "expected_failure_signature": payload.get("expected_failure_signature"),
            "quote_topology": payload.get("quote_topology"),
            "is_topology_branch": payload.get("is_topology_branch"),
        }

    def _infer_hypothesis_intents(self, payload: dict[str, Any]) -> list[str]:
        target_metrics = set(payload.get("target_metrics", {}))
        hard_guardrails = set(payload.get("hard_guardrails", {}))
        experiment_fields = target_metrics | hard_guardrails
        search_blob = " ".join(
            [
                str(payload.get("mutation_family") or ""),
                str(payload.get("title") or ""),
                str(payload.get("rationale") or ""),
                str(payload.get("expected_effect") or ""),
                str(payload.get("expected_failure_mode") or ""),
                str(payload.get("actual_failure_mode") or ""),
                _json_search_blob(payload.get("novelty_coordinates", {})),
            ]
        ).lower()
        intents: list[str] = []
        if payload.get("seed_eval_id") is not None or any(
            token in search_blob for token in ("refine", "continuation", "incumbent")
        ):
            intents.append("local_refine")
        if experiment_fields & {"arb_edge", "arb_loss_to_retail_gain"} or any(
            token in search_blob for token in ("anti-arb", "anti_arb", "arb", "toxic")
        ):
            intents.append("anti_arb")
        if experiment_fields & {
            "low_decile_mean_edge",
            "median_decile_mean_edge",
            "high_decile_mean_edge",
            "low_retail_mean_edge",
            "low_volatility_mean_edge",
        } or any(
            token in search_blob
            for token in ("weak-slice", "weak_slice", "low-retail", "low-vol", "tail")
        ):
            intents.append("weak_slice")
        if experiment_fields & {
            "time_weighted_bid_fee",
            "time_weighted_ask_fee",
            "max_fee_jump",
        } or any(
            token in search_blob
            for token in ("fee", "spike", "calm-flow", "calm_flow", "guardrail")
        ):
            intents.append("fee_discipline")
        if payload.get("novelty_coordinates") or any(
            token in search_blob
            for token in ("structural", "orthogonal", "pivot", "novel", "synth")
        ):
            intents.append("structural_pivot")
        return _sorted_unique(intents)

    def _hypothesis_time_marker(self, payload: dict[str, Any]) -> str:
        for field in ("updated_at", "created_at"):
            value = payload.get(field)
            if isinstance(value, str):
                return value
        return ""

    def _select_active_open_batch(
        self, hypotheses: dict[str, dict[str, Any]]
    ) -> tuple[str | None, str, list[dict[str, Any]]]:
        open_payloads = [
            payload
            for payload in hypotheses.values()
            if payload.get("status") in OPEN_HYPOTHESIS_STATUSES
        ]
        if not open_payloads:
            return None, "none", []
        grouped: dict[str, list[dict[str, Any]]] = {}
        for payload in open_payloads:
            batch_id = payload.get("batch_id")
            group_key = (
                batch_id
                if isinstance(batch_id, str) and batch_id.strip()
                else LEGACY_BATCH_KEY
            )
            grouped.setdefault(group_key, []).append(payload)
        active_group_key, active_payloads = max(
            grouped.items(),
            key=lambda item: (
                max(self._hypothesis_time_marker(payload) for payload in item[1]),
                item[0],
            ),
        )
        selection_mode = (
            "explicit_batch_id"
            if active_group_key != LEGACY_BATCH_KEY
            else "legacy_open_pool"
        )
        active_batch_id = (
            active_group_key if active_group_key != LEGACY_BATCH_KEY else None
        )
        return active_batch_id, selection_mode, active_payloads

    def _build_decomposition_coverage(
        self,
        hypotheses: dict[str, dict[str, Any]],
        *,
        active_open_ids: set[str],
    ) -> dict[str, dict[str, Any]]:
        coverage: dict[str, dict[str, Any]] = {
            layer: {"all_hypothesis_ids": [], "open_hypothesis_ids": []}
            for layer in DECOMPOSITION_LAYERS
        }
        coverage["unclassified"] = {"all_hypothesis_ids": [], "open_hypothesis_ids": []}
        for payload in hypotheses.values():
            layer = payload.get("primary_layer_changed")
            bucket_name = (
                layer
                if isinstance(layer, str) and layer in DECOMPOSITION_LAYERS
                else "unclassified"
            )
            bucket = coverage[bucket_name]
            bucket["all_hypothesis_ids"].append(payload["hypothesis_id"])
            if payload["hypothesis_id"] in active_open_ids:
                bucket["open_hypothesis_ids"].append(payload["hypothesis_id"])
        for bucket in coverage.values():
            bucket["all_hypothesis_ids"] = _sorted_unique(bucket["all_hypothesis_ids"])
            bucket["open_hypothesis_ids"] = _sorted_unique(
                bucket["open_hypothesis_ids"]
            )
        return coverage

    def _decomposition_gaps(
        self, decomposition_coverage: dict[str, dict[str, Any]]
    ) -> list[str]:
        return [
            layer
            for layer in DECOMPOSITION_LAYERS
            if not decomposition_coverage.get(layer, {}).get("open_hypothesis_ids")
        ]

    def _recent_unique_hypothesis_ids(
        self,
        results: list[dict[str, Any]],
        *,
        statuses: set[str],
        limit: int,
    ) -> list[str]:
        hypothesis_ids: list[str] = []
        seen: set[str] = set()
        for summary in reversed(results):
            if summary.get("status") not in statuses:
                continue
            hypothesis_id = summary.get("hypothesis_id")
            if not isinstance(hypothesis_id, str) or hypothesis_id in seen:
                continue
            hypothesis_ids.append(hypothesis_id)
            seen.add(hypothesis_id)
            if len(hypothesis_ids) >= limit:
                break
        return list(reversed(hypothesis_ids))

    def _near_replay_survivor_ids(
        self,
        results: list[dict[str, Any]],
        hypotheses: dict[str, dict[str, Any]],
    ) -> list[str]:
        survivor_ids = self._recent_unique_hypothesis_ids(
            results,
            statuses={"seed", "keep"},
            limit=2,
        )
        if len(survivor_ids) < 2:
            return []
        left = hypotheses.get(survivor_ids[0])
        right = hypotheses.get(survivor_ids[1])
        if left is None or right is None:
            return []
        left_key = self._same_spine_key(left)
        right_key = self._same_spine_key(right)
        if left_key is not None and left_key == right_key:
            return survivor_ids
        return []

    def _same_spine_key(self, payload: dict[str, Any]) -> tuple[str, str, str] | None:
        if payload.get("is_topology_branch") is True:
            return None
        primary_layer = payload.get("primary_layer_changed")
        held_layer = payload.get("layer_held_fixed")
        quote_topology = payload.get("quote_topology")
        if not isinstance(primary_layer, str):
            return None
        if not isinstance(held_layer, str):
            return None
        if not isinstance(quote_topology, str):
            return None
        return primary_layer, held_layer, quote_topology

    def _same_spine_group_label(self, spine_key: tuple[str, str, str]) -> str:
        primary_layer, held_layer, quote_topology = spine_key
        return f"{primary_layer}->{held_layer}:{quote_topology}"

    def _same_spine_failure_groups(
        self,
        results: list[dict[str, Any]],
        hypotheses: dict[str, dict[str, Any]],
    ) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {}
        seen: set[str] = set()
        for summary in reversed(results):
            if summary.get("status") not in {"discard", "invalid"}:
                continue
            hypothesis_id = summary.get("hypothesis_id")
            if not isinstance(hypothesis_id, str) or hypothesis_id in seen:
                continue
            seen.add(hypothesis_id)
            payload = hypotheses.get(hypothesis_id)
            if payload is None:
                continue
            spine_key = self._same_spine_key(payload)
            if spine_key is None:
                continue
            grouped.setdefault(self._same_spine_group_label(spine_key), []).append(
                hypothesis_id
            )
            if len(seen) >= SAME_SPINE_FAILURE_LOOKBACK:
                break
        return {
            group_label: _sorted_unique(hypothesis_ids)
            for group_label, hypothesis_ids in sorted(grouped.items())
            if len(_sorted_unique(hypothesis_ids)) >= 2
        }

    def _build_batch_diversity(
        self,
        *,
        batch_id: str | None,
        selection_mode: str,
        open_payloads: list[dict[str, Any]],
        results: list[dict[str, Any]],
        hypotheses: dict[str, dict[str, Any]],
        decomposition_coverage: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        open_primary_layers = sorted(
            {
                payload.get("primary_layer_changed")
                for payload in open_payloads
                if payload.get("primary_layer_changed") in DECOMPOSITION_LAYERS
            }
        )
        topology_branch_ids = _sorted_unique(
            [
                payload["hypothesis_id"]
                for payload in open_payloads
                if payload.get("is_topology_branch") is True
            ]
        )
        quote_topology_groups: dict[str, list[str]] = {}
        for payload in open_payloads:
            quote_topology = payload.get("quote_topology")
            if not isinstance(quote_topology, str):
                continue
            quote_topology_groups.setdefault(quote_topology, []).append(
                payload["hypothesis_id"]
            )
        quote_topology_groups = {
            quote_topology: _sorted_unique(hypothesis_ids)
            for quote_topology, hypothesis_ids in sorted(quote_topology_groups.items())
        }
        repeated_quote_topology_groups = {
            quote_topology: hypothesis_ids
            for quote_topology, hypothesis_ids in quote_topology_groups.items()
            if len(hypothesis_ids) >= 2
        }
        near_replay_survivor_ids = self._near_replay_survivor_ids(results, hypotheses)
        same_spine_failure_groups = self._same_spine_failure_groups(results, hypotheses)
        issues: list[str] = []
        if open_payloads and len(open_primary_layers) < 3:
            missing_layers = ", ".join(self._decomposition_gaps(decomposition_coverage))
            issues.append(
                "Open batch covers fewer than three primary layers"
                + (f"; missing: {missing_layers}" if missing_layers else "")
            )
        if open_payloads and not topology_branch_ids:
            issues.append("Open batch has no true topology branch")
        if len(open_payloads) >= 2 and len(quote_topology_groups) == 1:
            issues.append("Open batch stays inside a single quote topology")
        if near_replay_survivor_ids:
            issues.append(
                "Recent surviving branches are near-replays; pivot layers before another retune"
            )
        if same_spine_failure_groups:
            issues.append(
                "Recent failures cluster inside the same spine; pivot layers instead of replaying the spine"
            )
        return {
            "batch_id": batch_id,
            "selection_mode": selection_mode,
            "open_hypothesis_ids": _sorted_unique(
                [payload["hypothesis_id"] for payload in open_payloads]
            ),
            "open_primary_layers": open_primary_layers,
            "distinct_primary_layer_count": len(open_primary_layers),
            "has_topology_branch": bool(topology_branch_ids),
            "topology_branch_hypothesis_ids": topology_branch_ids,
            "quote_topology_groups": quote_topology_groups,
            "repeated_quote_topology_groups": repeated_quote_topology_groups,
            "near_replay_survivor_ids": near_replay_survivor_ids,
            "same_spine_failure_groups": same_spine_failure_groups,
            "force_layer_pivot": bool(
                near_replay_survivor_ids or same_spine_failure_groups
            ),
            "issues": issues,
        }

    def _structural_recommendations(
        self,
        *,
        decomposition_gaps: list[str],
        batch_diversity: dict[str, Any],
    ) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        if batch_diversity.get("force_layer_pivot"):
            recommendations.append(
                {
                    "kind": "layer_pivot",
                    "covered": False,
                    "reason": (
                        "Recent survivors or failures show same-spine replay pressure; "
                        "switch primary layer before another coefficient retune."
                    ),
                }
            )
        if (
            batch_diversity.get("open_hypothesis_ids")
            and batch_diversity.get("distinct_primary_layer_count", 0) < 3
            and decomposition_gaps
        ):
            recommendations.append(
                {
                    "kind": "decomposition_gap",
                    "covered": False,
                    "reason": (
                        "Open batch does not yet cover three distinct decomposition targets; "
                        f"next additions should include: {', '.join(decomposition_gaps)}."
                    ),
                }
            )
        if batch_diversity.get("open_hypothesis_ids") and not batch_diversity.get(
            "has_topology_branch"
        ):
            recommendations.append(
                {
                    "kind": "topology_branch",
                    "covered": False,
                    "reason": (
                        "Reserve at least one branch that changes how the quote is assembled, "
                        "not just how incumbent terms are tuned."
                    ),
                }
            )
        if not recommendations:
            recommendations.append(
                {
                    "kind": "batch_contract",
                    "covered": True,
                    "reason": "Open hypotheses satisfy the minimum layer and topology diversity contract.",
                }
            )
        return recommendations

    def _build_intent_coverage(
        self,
        hypotheses: dict[str, dict[str, Any]],
        *,
        active_open_ids: set[str],
    ) -> dict[str, dict[str, Any]]:
        coverage: dict[str, dict[str, Any]] = {
            intent: {"all_hypothesis_ids": [], "open_hypothesis_ids": []}
            for intent in PLANNING_INTENTS
        }
        for payload in hypotheses.values():
            for intent in self._infer_hypothesis_intents(payload):
                bucket = coverage.setdefault(
                    intent, {"all_hypothesis_ids": [], "open_hypothesis_ids": []}
                )
                bucket["all_hypothesis_ids"].append(payload["hypothesis_id"])
                if payload["hypothesis_id"] in active_open_ids:
                    bucket["open_hypothesis_ids"].append(payload["hypothesis_id"])
        for bucket in coverage.values():
            bucket["all_hypothesis_ids"] = _sorted_unique(bucket["all_hypothesis_ids"])
            bucket["open_hypothesis_ids"] = _sorted_unique(
                bucket["open_hypothesis_ids"]
            )
        return coverage

    def _portfolio_gaps(self, intent_coverage: dict[str, dict[str, Any]]) -> list[str]:
        return [
            intent
            for intent in PLANNING_INTENTS
            if intent != "local_refine"
            and not intent_coverage.get(intent, {}).get("open_hypothesis_ids")
        ]

    def _recommended_next_batch(
        self,
        *,
        frontier_bank: dict[str, Any],
        failure_clusters: dict[str, int],
        intent_coverage: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        best_raw = frontier_bank.get("best_raw", [])
        if best_raw:
            recommendations.append(
                {
                    "intent": "local_refine",
                    "covered": bool(
                        intent_coverage.get("local_refine", {}).get(
                            "open_hypothesis_ids"
                        )
                    ),
                    "reason": f"Exploit the strongest raw survivor {best_raw[0]['eval_id']} before widening again.",
                    "anchor_eval_id": best_raw[0]["eval_id"],
                }
            )
        intent_reasons = {
            "anti_arb": (
                "Arb leakage remains a distinct failure mode; keep one branch directly targeting arb_edge or arb_loss_to_retail_gain."
                if failure_clusters.get("arb_leak_regression", 0) > 0
                else "Keep one branch explicitly aimed at arb-loss improvement so cheaper calm quoting is not selected blindly."
            ),
            "weak_slice": "Keep one branch focused on weak low-retail, low-volatility, or tail slices instead of only overall mean_edge.",
            "fee_discipline": (
                "Recent failures show fee-surface shape matters; keep one branch constrained on average fee drift or max_fee_jump."
                if failure_clusters.get("over_spiky_fee_surface", 0) > 0
                or failure_clusters.get("overpriced_calm_flow", 0) > 0
                else "Keep one branch with explicit fee-discipline guardrails so structural pivots fail fast."
            ),
            "structural_pivot": "Reserve one orthogonal pivot so the batch does not collapse into semantically different versions of the same phenotype.",
        }
        for intent in ("anti_arb", "weak_slice", "fee_discipline", "structural_pivot"):
            recommendations.append(
                {
                    "intent": intent,
                    "covered": bool(
                        intent_coverage.get(intent, {}).get("open_hypothesis_ids")
                    ),
                    "reason": intent_reasons[intent],
                }
            )
        return recommendations

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
        self._ensure_read_surfaces(run_dir)
        self._sync_derived_views(run_dir)
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

    def _ensure_read_surfaces(self, run_dir: Path) -> None:
        _ensure_text_file(self._history_path(run_dir), "")
        self._hypotheses_dir(run_dir).mkdir(parents=True, exist_ok=True)
        _ensure_text_file(self._analysis_path(run_dir), _json_dump({}))

    def _read_results(self, run_dir: Path) -> list[dict[str, Any]]:
        return self._read_jsonl_records(run_dir / "results.jsonl")

    def _history_path(self, run_dir: Path) -> Path:
        return run_dir / "history.jsonl"

    def _analysis_path(self, run_dir: Path) -> Path:
        return run_dir / "analysis.json"

    def _read_jsonl_records(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise HillClimbHarnessError(
                    f"Invalid JSON in {path} line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(payload, dict):
                raise HillClimbHarnessError(
                    f"Expected JSON object in {path} line {line_number}"
                )
            records.append(payload)
        return records

    def _hypotheses_dir(self, run_dir: Path) -> Path:
        return run_dir / "hypotheses"

    def _hypothesis_path(self, run_dir: Path, hypothesis_id: str) -> Path:
        return self._hypotheses_dir(run_dir) / f"{hypothesis_id}.json"

    def _pending_sources_dir(self, run_dir: Path) -> Path:
        return run_dir / ".pending_sources"

    def _pending_source_path(
        self, run_dir: Path, *, stage: str, source_sha256: str
    ) -> Path:
        return self._pending_sources_dir(run_dir) / f"{stage}--{source_sha256}"

    def _normalize_string_list(self, values: list[str] | None) -> list[str]:
        if values is None:
            return []
        normalized: list[str] = []
        for value in values:
            if not isinstance(value, str):
                raise HillClimbHarnessError("Expected a list of strings")
            text = value.strip()
            if text:
                normalized.append(text)
        return normalized

    def _normalize_float_mapping(
        self,
        values: dict[str, float] | None,
        *,
        field_name: str,
        allowed_keys: tuple[str, ...] = EXPERIMENT_METRIC_FIELDS,
    ) -> dict[str, float]:
        if values is None:
            return {}
        if not isinstance(values, dict):
            raise HillClimbHarnessError(
                f"Expected {field_name} to be an object of finite numbers"
            )
        normalized: dict[str, float] = {}
        for key, value in values.items():
            if not isinstance(key, str) or not key.strip():
                raise HillClimbHarnessError(
                    f"Expected non-empty string keys in {field_name}"
                )
            if key not in allowed_keys:
                allowed = ", ".join(sorted(allowed_keys))
                raise HillClimbHarnessError(
                    f"Unknown {field_name} metric {key!r}; expected one of: {allowed}"
                )
            converted = _safe_float(value)
            if converted is None:
                raise HillClimbHarnessError(
                    f"Expected finite numeric value for {field_name} metric {key!r}"
                )
            normalized[key] = converted
        return normalized

    def _normalize_optional_text(
        self,
        value: str | None,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise HillClimbHarnessError(f"Expected {field_name} to be a string")
        normalized = value.strip()
        if not normalized:
            raise HillClimbHarnessError(f"Expected non-empty text for {field_name}")
        return normalized

    def _normalize_decomposition_layer(
        self,
        value: str | None,
        *,
        field_name: str,
    ) -> str | None:
        normalized = self._normalize_optional_text(value, field_name=field_name)
        if normalized is None:
            return None
        if normalized not in DECOMPOSITION_LAYERS:
            allowed = ", ".join(DECOMPOSITION_LAYERS)
            raise HillClimbHarnessError(
                f"Unknown {field_name} {normalized!r}; expected one of: {allowed}"
            )
        return normalized

    def _normalize_json_object(self, payload: dict[str, Any] | None) -> dict[str, Any]:
        if payload is None:
            return {}
        if not isinstance(payload, dict):
            raise HillClimbHarnessError("Expected a JSON object")
        try:
            json.dumps(payload, sort_keys=True)
        except TypeError as exc:
            raise HillClimbHarnessError("Expected a JSON-serializable object") from exc
        return dict(payload)

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
        profile: dict[str, float | None],
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
            tags.append("arb_leak_regression")
            notes.append("arb leakage worsened materially vs incumbent")
        low_slice_delta = deltas.get("low_retail_mean_edge")
        fee_delta = deltas.get("time_weighted_bid_fee")
        if (
            low_slice_delta is not None
            and low_slice_delta < -5.0
            and fee_delta is not None
            and fee_delta > 0.0005
        ):
            tags.append("overpriced_calm_flow")
            notes.append("calm-flow slice regressed while average fees moved up")
        max_fee_jump_delta = deltas.get("max_fee_jump")
        profile_max_fee_jump = _safe_float(profile.get("max_fee_jump"))
        if (max_fee_jump_delta is not None and max_fee_jump_delta > 0.0025) or (
            profile_max_fee_jump is not None and profile_max_fee_jump > 0.01
        ):
            tags.append("over_spiky_fee_surface")
            notes.append("fee jumps look too abrupt for viable screening")
        low_decile_delta = deltas.get("low_decile_mean_edge")
        high_decile_delta = deltas.get("high_decile_mean_edge")
        if (
            low_decile_delta is not None
            and low_decile_delta < -10.0
            and high_decile_delta is not None
            and high_decile_delta <= 0.0
        ):
            tags.append("tail_protection_loss")
            notes.append(
                "weak tail slices regressed without compensating strong-slice gain"
            )
        if overall_delta is not None and overall_delta <= 0.0:
            if any(
                (delta := deltas.get(field)) is not None and delta > 0.0
                for field in ("low_retail_mean_edge", "low_volatility_mean_edge")
            ):
                tags.append("weak_slice_improvement_without_overall_gain")
                notes.append(
                    "some weak slices improved but not enough to move overall edge"
                )
        primary_tag = tags[0] if tags else None
        if primary_tag is None and overall_delta is not None and overall_delta > 0.0:
            primary_tag = "improving_variant"
        return {
            "tags": _sorted_unique(tags),
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
                profile=profile,
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

    def _best_summary_for_metric(
        self, summaries: list[dict[str, Any]], metric: str, *, reverse: bool = True
    ) -> dict[str, Any] | None:
        best: dict[str, Any] | None = None
        best_value: float | None = None
        for summary in summaries:
            derived = summary.get("derived_analysis", {})
            profile = derived.get("profile", {}) if isinstance(derived, dict) else {}
            value = _safe_float(profile.get(metric))
            if value is None:
                continue
            if (
                best is None
                or best_value is None
                or (value > best_value if reverse else value < best_value)
            ):
                best = summary
                best_value = value
        return None if best is None else self._frontier_entry(best)

    def _frontier_entry(self, summary: dict[str, Any]) -> dict[str, Any]:
        derived = summary.get("derived_analysis", {})
        failure = (
            derived.get("failure_signature", {}) if isinstance(derived, dict) else {}
        )
        return {
            "eval_id": summary["eval_id"],
            "stage": summary["stage"],
            "status": summary["status"],
            "mean_edge": summary.get("mean_edge"),
            "hypothesis_id": summary.get("hypothesis_id"),
            "label": summary.get("label"),
            "profile": derived.get("profile", {}),
            "failure_tags": list(failure.get("tags", [])),
        }

    def _build_frontier_bank(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        valid = [
            summary
            for summary in results
            if summary.get("mean_edge") is not None
            and summary.get("status") != "invalid"
        ]
        sorted_by_edge = sorted(
            valid,
            key=lambda summary: float(summary["mean_edge"]),
            reverse=True,
        )
        incumbents = [
            self._frontier_entry(summary)
            for summary in valid
            if summary.get("status") in {"seed", "keep"}
        ]
        return {
            "incumbents": incumbents,
            "best_raw": [
                self._frontier_entry(summary) for summary in sorted_by_edge[:5]
            ],
            "best_low_retail": self._best_summary_for_metric(
                valid, "low_retail_mean_edge"
            ),
            "best_low_volatility": self._best_summary_for_metric(
                valid, "low_volatility_mean_edge"
            ),
            "best_anti_arb": self._best_summary_for_metric(valid, "arb_edge"),
            "best_fee_discipline": self._best_summary_for_metric(
                valid, "arb_loss_to_retail_gain", reverse=False
            ),
        }

    def _resolve_profile_input(
        self,
        *,
        stage: str,
        summary: dict[str, Any] | None,
        source_path: Path | str | None,
    ) -> dict[str, Any]:
        if summary is not None:
            summary_stage = summary.get("stage")
            if summary_stage != stage:
                raise HillClimbHarnessError(
                    f"Stored eval {summary.get('eval_id')!r} is for stage {summary_stage!r}, "
                    f"not requested stage {stage!r}"
                )
            derived = summary.get("derived_analysis", {})
            profile = derived.get("profile", {}) if isinstance(derived, dict) else {}
            if not isinstance(profile, dict):
                raise HillClimbHarnessError(
                    f"Stored eval {summary.get('eval_id')!r} is missing a usable profile"
                )
            return {
                "kind": "stored_eval",
                "eval_id": summary.get("eval_id"),
                "stage": stage,
                "label": summary.get("label"),
                "hypothesis_id": summary.get("hypothesis_id"),
                "profile": dict(profile),
            }
        if source_path is None:
            raise HillClimbHarnessError(
                "Expected either a stored summary or source path"
            )
        profile = self.profile_source(stage=stage, source_path=source_path)
        return {
            "kind": "ad_hoc_source",
            "eval_id": None,
            "stage": stage,
            "source_path": profile["source_path"],
            "strategy_name": profile["strategy_name"],
            "profile": profile["profile"],
        }

    def _read_run_context(
        self, run_id: str, *, allow_protected_surface_drift: bool
    ) -> dict[str, Any]:
        normalized_run_id = _slug(run_id, fallback="run")
        run_dir = self.artifact_root / normalized_run_id
        if not run_dir.exists():
            raise HillClimbHarnessError(f"Unknown hill-climb run: {normalized_run_id}")
        warnings = self._validate_current_run(
            run_dir,
            allow_protected_surface_drift=allow_protected_surface_drift,
        )
        return {
            "run_dir": run_dir,
            "results": self._read_results(run_dir),
            "state": self._load_state_payload(run_dir, require_current=True),
            "hypotheses": self._load_hypotheses(run_dir),
            "warnings": warnings,
        }

    def get_read_warnings(
        self, *, run_id: str, allow_protected_surface_drift: bool = False
    ) -> list[str]:
        """Return any non-fatal warnings for a read-only run inspection."""
        return list(
            self._read_run_context(
                run_id,
                allow_protected_surface_drift=allow_protected_surface_drift,
            )["warnings"]
        )

    def profile_source(self, *, stage: str, source_path: Path | str) -> dict[str, Any]:
        """Compile and evaluate a source without persisting a run artifact."""
        stage_config = resolve_hill_climb_stage(stage)
        source_path = Path(source_path)
        source_text = self._read_source(source_path)
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
            scorecard=scorecard,
        )
        return {
            "stage": stage_config.name,
            "source_path": str(source_path.resolve()),
            "strategy_name": strategy.get_name(),
            "profile": self._extract_profile(scorecard),
            "scorecard": scorecard,
        }

    def _load_hypotheses(self, run_dir: Path) -> dict[str, dict[str, Any]]:
        hypotheses_dir = self._hypotheses_dir(run_dir)
        if not hypotheses_dir.exists():
            return {}
        payloads: dict[str, dict[str, Any]] = {}
        for path in sorted(hypotheses_dir.glob("*.json")):
            payload = _json_load(path)
            hypothesis_id = payload.get("hypothesis_id")
            if not isinstance(hypothesis_id, str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has hypothesis file without hypothesis_id: {path.name}"
                )
            payloads[hypothesis_id] = payload
        return payloads

    def _write_hypothesis(self, run_dir: Path, payload: dict[str, Any]) -> None:
        path = self._hypothesis_path(run_dir, payload["hypothesis_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_json_dump(payload))

    def _build_history(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        history: list[dict[str, Any]] = []
        for summary in results:
            scorecard = summary.get("scorecard")
            gate = scorecard.get("gate", {}) if isinstance(scorecard, dict) else {}
            selection = summary.get("selection", {})
            derived = summary.get("derived_analysis", {})
            failure = (
                derived.get("failure_signature", {})
                if isinstance(derived, dict)
                else {}
            )
            history.append(
                {
                    "artifact_version": HISTORY_VERSION,
                    "eval_id": summary["eval_id"],
                    "created_at": summary["created_at"],
                    "stage": summary["stage"],
                    "status": summary["status"],
                    "label": summary.get("label"),
                    "description": summary.get("description"),
                    "hypothesis_id": summary.get("hypothesis_id"),
                    "source_sha256": summary.get("source_sha256"),
                    "parent_eval_id": summary.get("parent_eval_id"),
                    "parent_source_sha256": summary.get("parent_source_sha256"),
                    "mean_edge": summary.get("mean_edge"),
                    "delta_vs_incumbent": summary.get("delta_vs_incumbent"),
                    "promotion_margin": selection.get("promotion_margin"),
                    "gate_passed": bool(gate.get("passed", False)),
                    "decision_summary": selection.get("rationale")
                    or summary.get("error"),
                    "change_summary": summary.get("change_summary"),
                    "replay_reason": summary.get("replay_reason"),
                    "research_refs": list(summary.get("research_refs", [])),
                    "failure_tags": list(failure.get("tags", [])),
                    "primary_failure_tag": failure.get("primary_tag"),
                }
            )
        return history

    def _find_result(
        self, results: list[dict[str, Any]], eval_id: str
    ) -> dict[str, Any] | None:
        for summary in results:
            if summary["eval_id"] == eval_id:
                return summary
        return None

    def _resolve_lineage(
        self,
        run_dir: Path,
        *,
        hypothesis_id: str | None,
        parent_eval_id: str | None,
        stage: str,
        source_sha256: str,
        replay_reason: str | None,
    ) -> dict[str, Any]:
        with self._run_lock(run_dir):
            self._validate_current_run(run_dir)
            results = self._read_results(run_dir)
            state = self._load_state_payload(run_dir, require_current=True)
            hypotheses = self._load_hypotheses(run_dir)
            effective_hypothesis_id = hypothesis_id or state.get("next_hypothesis_id")
            if (
                effective_hypothesis_id is not None
                and effective_hypothesis_id not in hypotheses
            ):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has no hypothesis {effective_hypothesis_id!r}"
                )
            prior_eval_id: str | None = parent_eval_id
            if prior_eval_id is None:
                incumbent_before = self._read_incumbent(run_dir, stage)
                if incumbent_before is not None:
                    prior_eval_id = incumbent_before["eval_id"]
            parent_source_sha256 = None
            if prior_eval_id is not None:
                parent_summary = self._find_result(results, prior_eval_id)
                if parent_summary is None:
                    raise HillClimbHarnessError(
                        f"Run '{run_dir.name}' has no parent eval {prior_eval_id!r}"
                    )
                parent_source_sha256 = parent_summary.get("source_sha256")
            if replay_reason is None:
                for summary in results:
                    if (
                        summary.get("stage") == stage
                        and summary.get("source_sha256") == source_sha256
                    ):
                        raise HillClimbHarnessError(
                            "Same-stage duplicate source snapshots require an explicit replay reason. "
                            f"Run '{run_dir.name}' already recorded {summary['eval_id']} for stage "
                            f"{stage!r} with source {source_sha256}."
                        )
            if replay_reason is None:
                pending_path = self._pending_source_path(
                    run_dir, stage=stage, source_sha256=source_sha256
                )
                if pending_path.exists():
                    raise HillClimbHarnessError(
                        "Another evaluation is already in flight for the same stage/source snapshot. "
                        f"Run '{run_dir.name}' is currently reserving {stage!r} source {source_sha256}."
                    )
                pending_path.parent.mkdir(parents=True, exist_ok=True)
                pending_path.mkdir()
            return {
                "hypothesis_id": effective_hypothesis_id,
                "parent_eval_id": prior_eval_id,
                "parent_source_sha256": parent_source_sha256,
            }

    def _release_pending_source(
        self, run_dir: Path, *, stage: str, source_sha256: str
    ) -> None:
        pending_path = self._pending_source_path(
            run_dir, stage=stage, source_sha256=source_sha256
        )
        try:
            pending_path.rmdir()
        except FileNotFoundError:
            return
        try:
            self._pending_sources_dir(run_dir).rmdir()
        except OSError:
            return

    def _link_hypothesis_eval(self, run_dir: Path, summary: dict[str, Any]) -> None:
        hypothesis_id = summary.get("hypothesis_id")
        if hypothesis_id is None:
            return
        hypotheses = self._load_hypotheses(run_dir)
        payload = hypotheses.get(hypothesis_id)
        if payload is None:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has no hypothesis {hypothesis_id!r}"
            )
        updated = dict(payload)
        eval_ids = list(updated.get("eval_ids", []))
        if summary["eval_id"] not in eval_ids:
            eval_ids.append(summary["eval_id"])
        updated["eval_ids"] = eval_ids
        if updated.get("seed_eval_id") is None:
            updated["seed_eval_id"] = summary["eval_id"]
        updated["status"] = summary["status"]
        updated["updated_at"] = _utc_now()
        merged_refs = set(updated.get("research_refs", []))
        merged_refs.update(summary.get("research_refs", []))
        updated["research_refs"] = sorted(merged_refs)
        failure = summary.get("derived_analysis", {}).get("failure_signature", {})
        primary_failure = failure.get("primary_tag")
        if (
            summary.get("status") in {"discard", "invalid"}
            and isinstance(primary_failure, str)
            and primary_failure in (FAILURE_TAGS | {"invalid_eval"})
        ):
            updated["actual_failure_mode"] = primary_failure
        self._validate_hypothesis(run_dir, updated, results=self._read_results(run_dir))
        self._write_hypothesis(run_dir, updated)

    def _sync_derived_views(self, run_dir: Path) -> None:
        self._ensure_read_surfaces(run_dir)
        results = self._read_results(run_dir)
        hypotheses = self._load_hypotheses(run_dir)
        history_path = self._history_path(run_dir)
        history_lines = [
            json.dumps(entry, sort_keys=True) for entry in self._build_history(results)
        ]
        history_path.write_text(
            "" if not history_lines else "\n".join(history_lines) + "\n"
        )
        analysis_payload = self._build_run_analysis(
            run_dir=run_dir,
            results=results,
            hypotheses=hypotheses,
            warnings=[],
        )
        analysis_payload["generated_at"] = _utc_now()
        self._analysis_path(run_dir).write_text(_json_dump(analysis_payload))
        self._write_cross_run_index()

    def _collect_research_artifact_paths(self, run_dir: Path) -> list[str]:
        collected: set[str] = set()
        for summary in self._read_results(run_dir):
            for ref in summary.get("research_refs", []):
                if isinstance(ref, str) and ref.strip():
                    collected.add(ref)
        for payload in self._load_hypotheses(run_dir).values():
            for ref in payload.get("research_refs", []):
                if isinstance(ref, str) and ref.strip():
                    collected.add(ref)
        research_root = self.artifact_root.parent / "research"
        if research_root.exists():
            for path in sorted(research_root.iterdir()):
                if run_dir.name in path.name:
                    collected.add(str(path))
        return sorted(collected)

    def _write_cross_run_index(self) -> None:
        self.artifact_root.parent.mkdir(parents=True, exist_ok=True)
        entries: list[dict[str, Any]] = []
        if self.artifact_root.exists():
            for run_dir in sorted(
                path for path in self.artifact_root.iterdir() if path.is_dir()
            ):
                manifest_path = run_dir / "run.json"
                if not manifest_path.exists():
                    continue
                try:
                    manifest = _json_load(manifest_path)
                    results = self._read_results(run_dir)
                    state = self._load_state_payload(run_dir, require_current=False)
                    hypotheses = self._load_hypotheses(run_dir)
                    history = self._build_history(results)
                    analysis = self._build_run_analysis(
                        run_dir=run_dir,
                        results=results,
                        hypotheses=hypotheses,
                        warnings=[],
                    )
                    best_mean_edges = {
                        stage: float(summary["mean_edge"])
                        for stage, eval_id in state.get(
                            "incumbent_eval_ids", {}
                        ).items()
                        for summary in results
                        if summary["eval_id"] == eval_id
                        and summary.get("mean_edge") is not None
                    }
                    status = "active"
                    notes: list[str] = []
                    outcome_gate = state.get("outcome_gate")
                    if outcome_gate is not None:
                        gate_status = self._build_outcome_gate_status(state, results)
                        if gate_status is not None:
                            notes.append(gate_status.message)
                            if gate_status.passed:
                                status = "goal-passed"
                    if not history:
                        status = "empty"
                    elif any(entry["status"] == "invalid" for entry in history):
                        notes.append("contains invalid evaluations")
                    next_hypothesis_id = state.get("next_hypothesis_id")
                    if next_hypothesis_id is not None:
                        note = state.get("next_hypothesis_note")
                        if note:
                            notes.append(
                                f"next hypothesis {next_hypothesis_id}: {note}"
                            )
                        else:
                            notes.append(f"next hypothesis {next_hypothesis_id}")
                    entries.append(
                        {
                            "run_id": manifest["run_id"],
                            "created_at": manifest["created_at"],
                            "status": status,
                            "active_stage": state.get("current_target_stage"),
                            "best_eval_ids": dict(state.get("incumbent_eval_ids", {})),
                            "best_mean_edges": best_mean_edges,
                            "frontier_bank": analysis["frontier_bank"],
                            "failure_clusters": analysis["failure_clusters"],
                            "portfolio_gaps": analysis["portfolio_gaps"],
                            "research_artifact_paths": self._collect_research_artifact_paths(
                                run_dir
                            ),
                            "notes": notes,
                        }
                    )
                except HillClimbHarnessError as exc:
                    entries.append(
                        {
                            "run_id": run_dir.name,
                            "created_at": None,
                            "status": "invalid",
                            "active_stage": None,
                            "best_eval_ids": {},
                            "best_mean_edges": {},
                            "frontier_bank": {
                                "incumbents": [],
                                "best_raw": [],
                                "best_low_retail": None,
                                "best_low_volatility": None,
                                "best_anti_arb": None,
                                "best_fee_discipline": None,
                            },
                            "failure_clusters": {},
                            "portfolio_gaps": [],
                            "research_artifact_paths": [],
                            "notes": [str(exc)],
                        }
                    )
        current_run_id = None
        current_candidates = [
            entry
            for entry in entries
            if entry["status"] in {"active", "goal-passed"}
            and entry["created_at"] is not None
        ]
        if current_candidates:
            current_run_id = max(
                current_candidates,
                key=lambda entry: (entry["created_at"], entry["run_id"]),
            )["run_id"]
            for entry in entries:
                if entry["run_id"] == current_run_id:
                    continue
                if entry["status"] in {"active", "goal-passed"}:
                    entry["status"] = "historical"
                    entry["notes"] = [
                        f"superseded by retained lane {current_run_id}"
                    ] + entry["notes"]

        payload = {
            "artifact_version": CROSS_RUN_INDEX_VERSION,
            "generated_at": _utc_now(),
            "hill_climb_runs": entries,
        }
        (self.artifact_root.parent / "index.json").write_text(_json_dump(payload))

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

    def _build_gate(
        self,
        *,
        mean_edge: float,
        stage_config: Any,
        scorecard: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        thresholds: dict[str, float] = {}
        failures: list[str] = []
        if stage_config.min_mean_edge is not None:
            thresholds["mean_edge"] = stage_config.min_mean_edge
            if mean_edge < stage_config.min_mean_edge:
                failures.append(
                    f"mean_edge={mean_edge:.6f} is below stage threshold "
                    f"{stage_config.min_mean_edge:.6f}"
                )
        overall = scorecard.get("overall", {}) if isinstance(scorecard, dict) else {}
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
        return _json_load(incumbent_path)

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

    def _append_result(self, run_dir: Path, summary: dict[str, Any]) -> None:
        results_jsonl = run_dir / "results.jsonl"
        with results_jsonl.open("a") as handle:
            handle.write(json.dumps(summary, sort_keys=True) + "\n")
        self._append_results_row(run_dir, summary)

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
            "history_path": "history.jsonl",
            "hypotheses_dir": "hypotheses",
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

    def _evaluation_summary_base(
        self,
        *,
        run_id: str,
        eval_id: str,
        stage_config: Any,
        source_path: Path,
        source_sha256: str,
        snapshot_path: Path,
        label: str | None,
        description: str | None,
        lineage: dict[str, Any],
        change_summary: str | None,
        research_refs: list[str],
        replay_reason: str | None,
    ) -> dict[str, Any]:
        return {
            "artifact_version": ARTIFACT_VERSION,
            "run_id": run_id,
            "eval_id": eval_id,
            "created_at": _utc_now(),
            "stage": stage_config.name,
            "stage_description": stage_config.description,
            "source_path": str(source_path.resolve()),
            "source_sha256": source_sha256,
            "snapshot_path": str(snapshot_path),
            "snapshot_relpath": str(snapshot_path.relative_to(self.artifact_root / run_id)),
            "label": label,
            "description": description,
            "hypothesis_id": lineage["hypothesis_id"],
            "parent_eval_id": lineage["parent_eval_id"],
            "parent_source_sha256": lineage["parent_source_sha256"],
            "change_summary": change_summary,
            "research_refs": research_refs,
            "replay_reason": replay_reason,
        }

    def _default_state_payload(
        self, *, run_id: str, target_stage: str
    ) -> dict[str, Any]:
        return {
            "artifact_version": RUN_STATE_VERSION,
            "baseline_eval_id": None,
            "current_target_stage": target_stage,
            "incumbent_eval_ids": {},
            "last_completed_iteration": 0,
            "next_hypothesis_id": None,
            "next_hypothesis_note": None,
            "outcome_gate": None,
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
            "next_hypothesis_id": existing_state.get("next_hypothesis_id"),
            "next_hypothesis_note": existing_state.get("next_hypothesis_note"),
            "outcome_gate": existing_state.get("outcome_gate"),
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
        _ensure_text_file(run_dir / "results.jsonl", "")
        _ensure_text_file(run_dir / "results.tsv", RESULTS_HEADER)

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

    def _validate_current_run(
        self, run_dir: Path, *, allow_protected_surface_drift: bool = False
    ) -> list[str]:
        warnings: list[str] = []
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
            "history_path",
            "hypotheses_dir",
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
            ("history_path", "history.jsonl"),
            ("hypotheses_dir", "hypotheses"),
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
        hypotheses = self._load_hypotheses(run_dir)
        self._validate_hypotheses(run_dir, hypotheses, results)
        self._validate_history_index(run_dir, results)
        self._validate_snapshots(run_dir, results)
        try:
            self._protected_surface().verify_recorded_fingerprint(
                manifest.get("protected_surface_fingerprint"),
                run_id=run_dir.name,
            )
        except ProtectedSurfaceError as exc:
            if not allow_protected_surface_drift:
                raise HillClimbHarnessError(str(exc)) from exc
            warnings.append(str(exc))
        return warnings

    def _protected_surface(self) -> Any:
        if self._protected_surface_checker is None:
            self._protected_surface_checker = ProtectedSurfaceChecker.discover()
        return self._protected_surface_checker

    def _corrupted_run_message(self, run_dir: Path, problem: str) -> str:
        return (
            f"{problem}\n"
            "Do not hand-edit results.jsonl, results.tsv, state.json, or .next_eval_index to continue this run. "
            f"Quarantine the run directory and start a fresh run_id instead."
        )

    def _validate_results(self, run_dir: Path, results: list[dict[str, Any]]) -> None:
        seen_eval_ids: set[str] = set()
        seen_stage_sources: dict[tuple[str, str], str] = {}
        expected_index = 1
        eval_ids = {summary.get("eval_id") for summary in results}
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
                    self._corrupted_run_message(
                        run_dir,
                        f"Run '{run_dir.name}' contains duplicate eval_id {eval_id!r} in results.jsonl",
                    )
                )
            seen_eval_ids.add(eval_id)
            eval_stage, index = self._parse_eval_id(eval_id)
            if eval_stage != stage:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval_id {eval_id!r} that does not match stage {stage!r}"
                )
            if index != expected_index:
                raise HillClimbHarnessError(
                    self._corrupted_run_message(
                        run_dir,
                        f"Run '{run_dir.name}' has non-contiguous eval ids: expected index "
                        f"{expected_index:04d}, found {eval_id!r}",
                    )
                )
            expected_index += 1
            hypothesis_id = summary.get("hypothesis_id")
            if hypothesis_id is not None and not isinstance(hypothesis_id, str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {eval_id!r} with non-string hypothesis_id"
                )
            parent_eval_id = summary.get("parent_eval_id")
            if parent_eval_id is not None and not isinstance(parent_eval_id, str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {eval_id!r} with non-string parent_eval_id"
                )
            if parent_eval_id is not None and parent_eval_id not in eval_ids:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {eval_id!r} with unknown parent_eval_id {parent_eval_id!r}"
                )
            parent_source_sha256 = summary.get("parent_source_sha256")
            if parent_source_sha256 is not None and not isinstance(
                parent_source_sha256, str
            ):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {eval_id!r} with non-string parent_source_sha256"
                )
            if parent_eval_id is None and parent_source_sha256 is not None:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {eval_id!r} with parent_source_sha256 but no parent_eval_id"
                )
            if parent_eval_id is not None:
                parent_summary = next(
                    (
                        payload
                        for payload in results
                        if payload.get("eval_id") == parent_eval_id
                    ),
                    None,
                )
                if parent_summary is None or parent_source_sha256 != parent_summary.get(
                    "source_sha256"
                ):
                    raise HillClimbHarnessError(
                        f"Run '{run_dir.name}' has eval {eval_id!r} with stale parent_source_sha256"
                    )
            change_summary = summary.get("change_summary")
            if change_summary is not None and not isinstance(change_summary, str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {eval_id!r} with non-string change_summary"
                )
            replay_reason = summary.get("replay_reason")
            if replay_reason is not None and not isinstance(replay_reason, str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {eval_id!r} with non-string replay_reason"
                )
            research_refs = summary.get("research_refs", [])
            if not isinstance(research_refs, list) or any(
                not isinstance(value, str) for value in research_refs
            ):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {eval_id!r} with invalid research_refs"
                )
            source_sha256 = summary.get("source_sha256")
            if isinstance(source_sha256, str):
                key = (stage, source_sha256)
                prior_eval_id = seen_stage_sources.get(key)
                if prior_eval_id is not None and replay_reason is None:
                    raise HillClimbHarnessError(
                        self._corrupted_run_message(
                            run_dir,
                            f"Run '{run_dir.name}' reuses source_sha256 {source_sha256} for stage {stage!r} "
                            f"in {eval_id!r} after {prior_eval_id!r} without replay_reason",
                        )
                    )
                seen_stage_sources.setdefault(key, eval_id)

    def _validate_hypotheses(
        self,
        run_dir: Path,
        hypotheses: dict[str, dict[str, Any]],
        results: list[dict[str, Any]],
    ) -> None:
        for payload in hypotheses.values():
            self._validate_hypothesis(run_dir, payload, results=results)
            parent_hypothesis_id = payload.get("parent_hypothesis_id")
            if (
                parent_hypothesis_id is not None
                and parent_hypothesis_id not in hypotheses
            ):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has unknown parent_hypothesis_id "
                    f"{parent_hypothesis_id!r}"
                )
        state = self._load_state_payload(run_dir, require_current=True)
        next_hypothesis_id = state.get("next_hypothesis_id")
        if next_hypothesis_id is not None and next_hypothesis_id not in hypotheses:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' references missing next_hypothesis_id {next_hypothesis_id!r}"
            )
        for summary in results:
            hypothesis_id = summary.get("hypothesis_id")
            if hypothesis_id is not None and hypothesis_id not in hypotheses:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' has eval {summary['eval_id']!r} referencing missing hypothesis_id {hypothesis_id!r}"
                )

    def _validate_hypothesis(
        self,
        run_dir: Path,
        payload: dict[str, Any],
        *,
        results: list[dict[str, Any]],
    ) -> None:
        payload.setdefault("target_metrics", {})
        payload.setdefault("hard_guardrails", {})
        payload.setdefault("expected_failure_mode", None)
        payload.setdefault("actual_failure_mode", None)
        payload.setdefault("novelty_coordinates", {})
        payload.setdefault("synthesis_eligible", True)
        payload.setdefault("nearest_prior_failures", [])
        payload.setdefault("nearest_prior_successes", [])
        payload.setdefault("batch_id", None)
        payload.setdefault("primary_layer_changed", None)
        payload.setdefault("layer_held_fixed", None)
        payload.setdefault("hidden_coupling_removed", None)
        payload.setdefault("why_not_coefficient_retune", None)
        payload.setdefault("expected_win_condition", None)
        payload.setdefault("expected_failure_signature", None)
        payload.setdefault("quote_topology", None)
        payload.setdefault("is_topology_branch", None)
        required_fields = {
            "artifact_version",
            "hypothesis_id",
            "title",
            "rationale",
            "expected_effect",
            "mutation_family",
            "status",
            "batch_id",
            "created_at",
            "updated_at",
            "parent_hypothesis_id",
            "seed_eval_id",
            "eval_ids",
            "research_refs",
            "target_metrics",
            "hard_guardrails",
            "expected_failure_mode",
            "actual_failure_mode",
            "novelty_coordinates",
            "synthesis_eligible",
            "nearest_prior_failures",
            "nearest_prior_successes",
            "primary_layer_changed",
            "layer_held_fixed",
            "hidden_coupling_removed",
            "why_not_coefficient_retune",
            "expected_win_condition",
            "expected_failure_signature",
            "quote_topology",
            "is_topology_branch",
        }
        missing = sorted(required_fields - set(payload))
        if missing:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload.get('hypothesis_id')!r} is missing required fields: {', '.join(missing)}"
            )
        if payload["artifact_version"] != HYPOTHESIS_VERSION:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has unsupported version {payload['artifact_version']!r}"
            )
        for field in (
            "hypothesis_id",
            "title",
            "rationale",
            "expected_effect",
            "mutation_family",
            "status",
            "created_at",
            "updated_at",
        ):
            if not isinstance(payload[field], str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' hypothesis field {field!r} must be a string"
                )
        for field in (
            "hidden_coupling_removed",
            "why_not_coefficient_retune",
            "expected_win_condition",
            "expected_failure_signature",
            "quote_topology",
        ):
            value = payload[field]
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid {field}"
                )
        for field in ("primary_layer_changed", "layer_held_fixed"):
            value = payload[field]
            if value is not None and value not in DECOMPOSITION_LAYERS:
                allowed = ", ".join(DECOMPOSITION_LAYERS)
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has unknown {field} {value!r}; "
                    f"expected one of: {allowed}"
                )
        if (
            payload["primary_layer_changed"] is not None
            and payload["layer_held_fixed"] is not None
            and payload["primary_layer_changed"] == payload["layer_held_fixed"]
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} cannot change and hold fixed the same layer"
            )
        if payload["is_topology_branch"] is not None and not isinstance(
            payload["is_topology_branch"], bool
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid is_topology_branch"
            )
        if payload["status"] not in HYPOTHESIS_STATUSES:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has unsupported status {payload['status']!r}"
            )
        if payload["batch_id"] is not None and (
            not isinstance(payload["batch_id"], str) or not payload["batch_id"].strip()
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid batch_id"
            )
        if payload["parent_hypothesis_id"] is not None and not isinstance(
            payload["parent_hypothesis_id"], str
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid parent_hypothesis_id"
            )
        if payload["seed_eval_id"] is not None and not isinstance(
            payload["seed_eval_id"], str
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid seed_eval_id"
            )
        if not isinstance(payload["eval_ids"], list) or any(
            not isinstance(eval_id, str) for eval_id in payload["eval_ids"]
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid eval_ids"
            )
        if not isinstance(payload["research_refs"], list) or any(
            not isinstance(reference, str) for reference in payload["research_refs"]
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid research_refs"
            )
        if not isinstance(payload["target_metrics"], dict) or any(
            not isinstance(key, str)
            or key not in EXPERIMENT_METRIC_FIELDS
            or _safe_float(value) is None
            for key, value in payload["target_metrics"].items()
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid target_metrics"
            )
        if not isinstance(payload["hard_guardrails"], dict) or any(
            not isinstance(key, str)
            or key not in EXPERIMENT_METRIC_FIELDS
            or _safe_float(value) is None
            for key, value in payload["hard_guardrails"].items()
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid hard_guardrails"
            )
        for field in ("expected_failure_mode", "actual_failure_mode"):
            if payload[field] is not None and not isinstance(payload[field], str):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid {field}"
                )
            if payload[field] is not None and payload[field] not in VALID_FAILURE_MODES:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has unknown {field}"
                )
        if not isinstance(payload["novelty_coordinates"], dict):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid novelty_coordinates"
            )
        try:
            json.dumps(payload["novelty_coordinates"], sort_keys=True)
        except TypeError as exc:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has non-serializable novelty_coordinates"
            ) from exc
        if not isinstance(payload["synthesis_eligible"], bool):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid synthesis_eligible"
            )
        for field in ("nearest_prior_failures", "nearest_prior_successes"):
            if not isinstance(payload[field], list) or any(
                not isinstance(value, str) for value in payload[field]
            ):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has invalid {field}"
                )
        result_eval_ids = {summary["eval_id"] for summary in results}
        if (
            payload["seed_eval_id"] is not None
            and payload["seed_eval_id"] not in result_eval_ids
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} has unknown seed_eval_id {payload['seed_eval_id']!r}"
            )
        if any(eval_id not in result_eval_ids for eval_id in payload["eval_ids"]):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' hypothesis {payload['hypothesis_id']!r} references unknown eval_ids"
            )

    def _validate_history_index(
        self, run_dir: Path, results: list[dict[str, Any]]
    ) -> None:
        history_path = self._history_path(run_dir)
        if not history_path.exists():
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' is missing history.jsonl"
            )
        actual = self._read_jsonl_records(history_path)
        expected = self._build_history(results)
        if actual != expected:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"Run '{run_dir.name}' has stale history.jsonl",
                )
            )

    def _validate_continuity_files(
        self, run_dir: Path, results: list[dict[str, Any]]
    ) -> None:
        legacy_counter = run_dir / LEGACY_NEXT_EVAL_ID_FILENAME
        if legacy_counter.exists():
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"Run '{run_dir.name}' still has obsolete continuity file {LEGACY_NEXT_EVAL_ID_FILENAME!r}. "
                    "Retained runs with the old continuity file are unsupported.",
                )
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
                self._corrupted_run_message(
                    run_dir,
                    f"Run '{run_dir.name}' has stale {NEXT_EVAL_INDEX_FILENAME!r}: "
                    f"expected {expected_next}, found {next_eval_index}",
                )
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
            "next_hypothesis_id",
            "next_hypothesis_note",
            "outcome_gate",
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
        self._validate_stop_rules(run_dir, state["stop_rules"])
        self._validate_outcome_gate(run_dir, state["outcome_gate"])
        if state["run_mode"] not in {"foreground", "background"}:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' has unsupported run_mode {state['run_mode']!r}"
            )
        if state["next_hypothesis_id"] is not None and not isinstance(
            state["next_hypothesis_id"], str
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' state field next_hypothesis_id must be null or a string"
            )
        if state["next_hypothesis_note"] is not None and not isinstance(
            state["next_hypothesis_note"], str
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' state field next_hypothesis_note must be null or a string"
            )
        if (
            state["next_hypothesis_id"] is None
            and state["next_hypothesis_note"] is not None
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' cannot retain next_hypothesis_note without next_hypothesis_id"
            )
        if state["next_hypothesis_id"] is not None:
            hypotheses = self._load_hypotheses(run_dir)
            if state["next_hypothesis_id"] not in hypotheses:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' references missing next_hypothesis_id {state['next_hypothesis_id']!r}"
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
                self._corrupted_run_message(
                    run_dir,
                    f"Run '{run_dir.name}' has stale baseline_eval_id: expected {expected_baseline!r}, "
                    f"found {state['baseline_eval_id']!r}",
                )
            )
        if state["last_completed_iteration"] != len(results):
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"Run '{run_dir.name}' has stale last_completed_iteration: expected {len(results)}, "
                    f"found {state['last_completed_iteration']}",
                )
            )
        expected_incumbents: dict[str, str] = {}
        for summary in results:
            if summary["status"] in {"seed", "keep"}:
                expected_incumbents[summary["stage"]] = summary["eval_id"]
        if state["incumbent_eval_ids"] != expected_incumbents:
            raise HillClimbHarnessError(
                self._corrupted_run_message(
                    run_dir,
                    f"Run '{run_dir.name}' has stale incumbent_eval_ids in state.json",
                )
            )

    def _validate_outcome_gate(
        self, run_dir: Path, outcome_gate: object
    ) -> None:
        if outcome_gate is None:
            return
        if not isinstance(outcome_gate, Mapping):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' state field outcome_gate must be null or an object"
            )
        outcome_gate_payload = dict(outcome_gate)
        stage = outcome_gate_payload.get("stage")
        if stage not in HILL_CLIMB_STAGES:
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' outcome_gate has unknown stage {stage!r}"
            )
        minimum_mean_edge = outcome_gate_payload.get("minimum_mean_edge")
        if isinstance(minimum_mean_edge, bool) or not isinstance(
            minimum_mean_edge, (int, float)
        ):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' outcome_gate.minimum_mean_edge must be a finite number"
            )
        if not math.isfinite(float(minimum_mean_edge)):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' outcome_gate.minimum_mean_edge must be a finite number"
            )

    def _validate_stop_rules(self, run_dir: Path, stop_rules: object) -> None:
        if not isinstance(stop_rules, Mapping):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' state field stop_rules must be an object"
            )
        stop_rule_payload = dict(stop_rules)
        expected_keys = set(DEFAULT_STOP_RULES)
        actual_keys = set(stop_rule_payload)
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        if missing or extra:
            details: list[str] = []
            if missing:
                details.append(f"missing: {', '.join(missing)}")
            if extra:
                details.append(f"unknown: {', '.join(extra)}")
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' stop_rules must match the current contract ({'; '.join(details)})"
            )
        validated_values: dict[str, int] = {}
        for key, minimum in DEFAULT_STOP_RULES.items():
            raw_value = stop_rule_payload[key]
            if isinstance(raw_value, bool) or not isinstance(raw_value, int):
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' stop_rules[{key!r}] must be an integer >= {minimum}"
                )
            if raw_value < minimum:
                raise HillClimbHarnessError(
                    f"Run '{run_dir.name}' stop_rules[{key!r}] must be an integer >= {minimum}"
                )
            validated_values[key] = raw_value
        refine_after = validated_values["refine_after_non_improving_iterations"]
        pivot_after = validated_values["pivot_after_non_improving_iterations"]
        stop_after = validated_values["stop_after_non_improving_iterations"]
        if not (refine_after <= pivot_after <= stop_after):
            raise HillClimbHarnessError(
                f"Run '{run_dir.name}' stop_rules must satisfy refine <= pivot <= stop"
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
            next_hypothesis_id=state["next_hypothesis_id"],
            next_hypothesis_note=state["next_hypothesis_note"],
            run_mode=state["run_mode"],
            stop_rules=dict(state["stop_rules"]),
            updated_at=state["updated_at"],
            outcome_gate=self._build_outcome_gate_status(state, results),
            guidance=guidance,
        )

    def _build_outcome_gate_status(
        self,
        state: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> OutcomeGateStatus | None:
        raw_outcome_gate = state.get("outcome_gate")
        if raw_outcome_gate is None:
            return None

        stage = raw_outcome_gate["stage"]
        minimum_mean_edge = float(raw_outcome_gate["minimum_mean_edge"])
        incumbent: dict[str, Any] | None = None
        for summary in results:
            if summary["stage"] == stage and summary["status"] in {"seed", "keep"}:
                incumbent = summary
        if incumbent is None:
            return OutcomeGateStatus(
                stage=stage,
                minimum_mean_edge=minimum_mean_edge,
                incumbent_mean_edge=None,
                passed=False,
                message=(
                    f"pending (no {stage} incumbent yet; target {minimum_mean_edge:.6f})"
                ),
            )

        incumbent_mean_edge = float(incumbent["mean_edge"])
        if incumbent_mean_edge >= minimum_mean_edge:
            return OutcomeGateStatus(
                stage=stage,
                minimum_mean_edge=minimum_mean_edge,
                incumbent_mean_edge=incumbent_mean_edge,
                passed=True,
                message=(
                    f"passed ({stage} incumbent {incumbent_mean_edge:.6f} cleared target "
                    f"{minimum_mean_edge:.6f})"
                ),
            )
        return OutcomeGateStatus(
            stage=stage,
            minimum_mean_edge=minimum_mean_edge,
            incumbent_mean_edge=incumbent_mean_edge,
            passed=False,
            message=(
                f"pending ({stage} incumbent {incumbent_mean_edge:.6f} is below target "
                f"{minimum_mean_edge:.6f})"
            ),
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
