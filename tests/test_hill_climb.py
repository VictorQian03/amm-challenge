"""Tests for the hill-climb research harness."""

import argparse
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import threading
from typing import Any, cast

import pytest

from amm_competition.cli import (
    hill_climb_analyze_run_command,
    hill_climb_compare_profiles_command,
    hill_climb_eval_command,
    hill_climb_history_command,
    hill_climb_set_state_command,
    hill_climb_set_hypothesis_command,
    hill_climb_show_eval_command,
    hill_climb_show_hypothesis_command,
    hill_climb_status_command,
    hill_climb_summarize_run_command,
)
from amm_competition.competition.match import LightweightSimResult, MatchResult
from amm_competition.competition.protected_surface import (
    ProtectedSurfaceChecker,
    ProtectedSurfaceFingerprint,
)
from amm_competition.hill_climb.harness import (
    DEFAULT_STOP_RULES,
    HillClimbHarness,
    HillClimbHarnessError,
    INCUMBENT_EPSILON,
    LEGACY_NEXT_EVAL_ID_FILENAME,
    RUN_MANIFEST_VERSION,
    RUN_STATE_VERSION,
)
from amm_competition.hill_climb.stages import (
    HILL_CLIMB_STAGES,
    build_stage_config,
    build_stage_runner,
)


def _make_match_result(*, mean_edges: list[float]) -> MatchResult:
    simulation_results = []
    for seed, candidate_edge in enumerate(mean_edges):
        benchmark_edge = candidate_edge - 1.0
        simulation_results.append(
            LightweightSimResult(
                seed=seed,
                strategies=["submission", "normalizer"],
                pnl={
                    "submission": Decimal(str(candidate_edge)),
                    "normalizer": Decimal(str(benchmark_edge)),
                },
                edges={
                    "submission": Decimal(str(candidate_edge)),
                    "normalizer": Decimal(str(benchmark_edge)),
                },
                initial_fair_price=100.0,
                initial_reserves={
                    "submission": (100.0, 10000.0),
                    "normalizer": (100.0, 10000.0),
                },
                steps=[],
                arb_volume_y={"submission": 2.0, "normalizer": 1.0},
                retail_volume_y={"submission": 10.0, "normalizer": 5.0},
                average_fees={
                    "submission": (0.0075, 0.0075),
                    "normalizer": (0.003, 0.003),
                },
                gbm_sigma=0.00095,
                retail_arrival_rate=0.8,
                retail_mean_size=20.0,
                retail_edge={"submission": 5.0, "normalizer": 4.0},
                arb_edge={"submission": -1.0, "normalizer": -1.0},
                retail_trade_count={"submission": 3, "normalizer": 2},
                arb_trade_count={"submission": 1, "normalizer": 1},
                max_fee_jump={"submission": 0.001, "normalizer": 0.0},
                time_weighted_fees={
                    "submission": (0.0075, 0.0075),
                    "normalizer": (0.003, 0.003),
                },
            )
        )

    return MatchResult(
        strategy_a="candidate",
        strategy_b="normalizer",
        wins_a=len(mean_edges),
        wins_b=0,
        draws=0,
        total_pnl_a=sum(
            (result.pnl["submission"] for result in simulation_results), Decimal("0")
        ),
        total_pnl_b=sum(
            (result.pnl["normalizer"] for result in simulation_results), Decimal("0")
        ),
        total_edge_a=sum(
            (result.edges["submission"] for result in simulation_results), Decimal("0")
        ),
        total_edge_b=sum(
            (result.edges["normalizer"] for result in simulation_results), Decimal("0")
        ),
        simulation_results=simulation_results,
    )


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _git(args: list[str], *, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def _build_protected_repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    protected_path = repo_root / "amm_competition" / "competition" / "config.py"
    strategy_path = repo_root / "contracts" / "src" / "Strategy.sol"
    protected_path.parent.mkdir(parents=True)
    strategy_path.parent.mkdir(parents=True)
    (repo_root / ".competition-protected-paths").write_text(
        "amm_competition/competition/config.py\n"
    )
    protected_path.write_text("BASELINE = 1\n")
    strategy_path.write_text("// strategy\n")

    _git(["git", "init"], cwd=repo_root)
    _git(["git", "config", "user.name", "Test User"], cwd=repo_root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=repo_root)
    _git(["git", "add", "."], cwd=repo_root)
    _git(["git", "commit", "-m", "init"], cwd=repo_root)
    return repo_root, strategy_path, protected_path


class _StubStrategy:
    def __init__(self, name: str = "Candidate") -> None:
        self._name = name

    def get_name(self) -> str:
        return self._name


class _FixedStrategyLoader:
    def __init__(self, strategy: _StubStrategy | None = None) -> None:
        self._strategy = strategy or _StubStrategy()

    def __call__(self, source_text: str) -> _StubStrategy:
        del source_text
        return self._strategy


class _SequentialStrategyLoader:
    def __init__(self, outcomes: list[_StubStrategy | BaseException]) -> None:
        self._outcomes = iter(outcomes)

    def __call__(self, source_text: str) -> _StubStrategy:
        del source_text
        outcome = next(self._outcomes)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class _SequentialRunnerFactory:
    def __init__(self, results: list[MatchResult]) -> None:
        self._results = iter(results)

    def __call__(self, stage: str, n_workers: int | None) -> "_SequentialRunnerFactory":
        del stage, n_workers
        return self

    def run_match(self, strategy_a, strategy_b, store_results=False) -> MatchResult:
        del strategy_a, strategy_b, store_results
        return next(self._results)


class _NoopProtectedSurfaceChecker:
    def ensure_runtime_eval_allowed(self) -> None:
        return None

    def current_fingerprint(self) -> ProtectedSurfaceFingerprint:
        return ProtectedSurfaceFingerprint(
            manifest_path=".competition-protected-paths",
            sha256="test-fingerprint",
            file_count=1,
        )

    def verify_recorded_fingerprint(
        self, recorded_payload: object, *, run_id: str
    ) -> None:
        del run_id
        if recorded_payload != self.current_fingerprint().to_payload():
            raise RuntimeError("unexpected test fingerprint mismatch")


def _build_test_harness(
    tmp_path: Path,
    *,
    strategy_loader=None,
    match_results: list[MatchResult] | None = None,
) -> HillClimbHarness:
    return HillClimbHarness(
        artifact_root=tmp_path / "artifacts",
        n_workers=1,
        strategy_loader=cast(Any, strategy_loader or _FixedStrategyLoader()),
        baseline_loader=lambda: object(),
        stage_runner_factory=_SequentialRunnerFactory(
            match_results or [_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])]
        ),
        protected_surface_checker=_NoopProtectedSurfaceChecker(),
    )


def _structural_hypothesis_kwargs(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "batch_id": "batch-001",
        "primary_layer_changed": "risk_budget",
        "layer_held_fixed": "quote_map",
        "hidden_coupling_removed": "Risk widening and cheap-mode release share one trigger.",
        "why_not_coefficient_retune": "The branch changes the control split rather than rescaling the incumbent overlay stack.",
        "expected_win_condition": "Improve screen mean_edge without broad calm-flow repricing.",
        "expected_failure_signature": "Arb leakage improves little while fees still widen too abruptly.",
        "quote_topology": "split-budget",
        "is_topology_branch": False,
    }
    payload.update(overrides)
    return payload


def test_hill_climb_stages_keep_competition_length_steps():
    cfg = build_stage_config()
    assert cfg.n_steps == 10000
    for stage in HILL_CLIMB_STAGES.values():
        assert len(stage.seed_block) == stage.n_simulations


def test_build_stage_runner_uses_hill_climb_stage_seed_block():
    runner = build_stage_runner("climb", n_workers=1)
    assert runner.n_simulations == HILL_CLIMB_STAGES["climb"].n_simulations
    assert runner.seed_block == HILL_CLIMB_STAGES["climb"].seed_block


def test_evaluate_records_seed_keep_and_discard(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
            _make_match_result(mean_edges=[5.5, 5.5, 5.5, 5.5]),
        ],
    )

    first = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        label="baseline",
    )
    source_path.write_text("// candidate v2")
    second = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        label="improved",
    )
    source_path.write_text("// candidate v3")
    third = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        label="regression",
    )

    assert first["status"] == "seed"
    assert first["scorecard"]["run_metadata"]["stage"] == "screen"
    assert first["scorecard"]["gate"]["passed"] is True
    assert second["status"] == "keep"
    assert second["delta_vs_incumbent"] == pytest.approx(1.0)
    assert second["selection"]["promotion_margin"] == pytest.approx(INCUMBENT_EPSILON)
    assert third["status"] == "discard"
    assert third["delta_vs_incumbent"] == pytest.approx(-0.5)

    results_path = tmp_path / "artifacts" / "mar26" / "results.tsv"
    results = results_path.read_text().splitlines()
    assert len(results) == 4
    assert results[0].startswith("eval_id\tstage\tstatus")

    incumbent_path = tmp_path / "artifacts" / "mar26" / "incumbents" / "screen.json"
    incumbent = json.loads(incumbent_path.read_text())
    assert incumbent["eval_id"] == second["eval_id"]
    assert incumbent["status"] == "keep"
    assert second["derived_analysis"]["profile"]["mean_edge"] == pytest.approx(6.0)
    assert "failure_signature" in third["derived_analysis"]


def test_evaluate_writes_current_manifest_and_state(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(tmp_path)

    summary = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    run_dir = tmp_path / "artifacts" / "mar26"
    manifest = _load_json(run_dir / "run.json")
    state = _load_json(run_dir / "state.json")

    assert manifest["artifact_version"] == RUN_MANIFEST_VERSION
    assert manifest["active_strategy_path"] == str(source_path.resolve())
    assert manifest["continuity_counter"] == ".next_eval_index"
    assert manifest["history_path"] == "history.jsonl"
    assert manifest["hypotheses_dir"] == "hypotheses"
    assert manifest["protected_surface_fingerprint"] == {
        "manifest_path": ".competition-protected-paths",
        "sha256": "test-fingerprint",
        "file_count": 1,
    }
    assert state["artifact_version"] == RUN_STATE_VERSION
    assert state["baseline_eval_id"] == summary["eval_id"]
    assert state["incumbent_eval_ids"] == {"screen": summary["eval_id"]}
    assert state["last_completed_iteration"] == 1
    assert state["current_target_stage"] == "screen"
    assert state["next_hypothesis_id"] is None
    assert state["next_hypothesis_note"] is None
    assert state["stop_rules"] == DEFAULT_STOP_RULES
    assert (run_dir / ".next_eval_index").read_text().strip() == "2"
    assert (run_dir / "history.jsonl").exists()
    assert (run_dir / "hypotheses").is_dir()
    assert (tmp_path / "index.json").exists()


def test_evaluate_writes_invalid_record_on_failure(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// invalid candidate")

    harness = _build_test_harness(
        tmp_path,
        strategy_loader=_SequentialStrategyLoader(
            [HillClimbHarnessError("bad strategy")]
        ),
    )

    with pytest.raises(HillClimbHarnessError, match="bad strategy"):
        harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    results_jsonl = tmp_path / "artifacts" / "mar26" / "results.jsonl"
    payload = json.loads(results_jsonl.read_text().splitlines()[0])
    assert payload["status"] == "invalid"
    assert payload["error"] == "bad strategy"


def test_baseline_eval_id_skips_initial_invalid_result(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        strategy_loader=_SequentialStrategyLoader(
            [HillClimbHarnessError("bad strategy"), _StubStrategy()]
        ),
    )

    with pytest.raises(HillClimbHarnessError, match="bad strategy"):
        harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    source_path.write_text("// candidate retry")
    summary = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    state = _load_json(tmp_path / "artifacts" / "mar26" / "state.json")

    assert summary["status"] == "seed"
    assert state["baseline_eval_id"] == summary["eval_id"]
    assert state["last_completed_iteration"] == 2


def test_evaluate_reuses_content_addressed_snapshot(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
        ],
    )

    first = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    second = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        replay_reason="intentional replay of identical source for snapshot reuse",
    )

    assert first["snapshot_path"] == second["snapshot_path"]
    assert Path(first["snapshot_path"]).parent.name == "snapshots"
    assert not (tmp_path / "artifacts" / "mar26" / "evaluations").exists()


def test_evaluate_rejects_same_stage_duplicate_source_without_replay_reason(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
        ],
    )

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    with pytest.raises(HillClimbHarnessError, match="duplicate source snapshots"):
        harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)


def test_evaluate_records_lineage_metadata_and_updates_history_and_hypothesis_registry(
    tmp_path,
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate baseline")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
        ],
    )

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="timing-overlay",
        title="Timing overlay",
        rationale="Shorten the widening lag",
        expected_effect="Improve clustered toxic handling",
        mutation_family="timing-overlay",
        status="queued",
        research_refs=["docs/plans/active/apr01-screen420-2134.md"],
        **_structural_hypothesis_kwargs(),
    )

    source_path.write_text("// candidate mutated")
    summary = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        hypothesis_id="timing-overlay",
        parent_eval_id="screen_0001",
        change_summary="Shorten the widening lag after clustered shocks",
        research_refs=["artifacts/research/run-a/memo.md"],
    )

    assert summary["hypothesis_id"] == "timing-overlay"
    assert summary["parent_eval_id"] == "screen_0001"
    assert summary["parent_source_sha256"] is not None
    assert (
        summary["change_summary"] == "Shorten the widening lag after clustered shocks"
    )
    assert summary["research_refs"] == ["artifacts/research/run-a/memo.md"]

    history = harness.get_history(run_id="mar26")
    assert history[-1]["hypothesis_id"] == "timing-overlay"
    assert history[-1]["parent_eval_id"] == "screen_0001"
    assert (
        history[-1]["change_summary"]
        == "Shorten the widening lag after clustered shocks"
    )

    hypothesis = harness.get_hypothesis(run_id="mar26", hypothesis_id="timing-overlay")
    assert hypothesis["seed_eval_id"] == "screen_0002"
    assert hypothesis["eval_ids"] == ["screen_0002"]
    assert hypothesis["status"] == "keep"
    assert sorted(hypothesis["research_refs"]) == [
        "artifacts/research/run-a/memo.md",
        "docs/plans/active/apr01-screen420-2134.md",
    ]

    index_payload = json.loads((tmp_path / "index.json").read_text())
    assert index_payload["artifact_version"]
    assert index_payload["hill_climb_runs"][0]["run_id"] == "mar26"


def test_evaluate_discards_when_stage_gate_fails(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[_make_match_result(mean_edges=[-0.5, -0.5, -0.5, -0.5])],
    )

    summary = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        label="negative",
    )

    assert summary["status"] == "discard"
    assert summary["delta_vs_incumbent"] is None
    assert summary["selection"]["promotion_margin"] is None
    assert summary["scorecard"]["gate"]["passed"] is False
    assert "below stage threshold" in summary["scorecard"]["gate"]["failures"][0]


def test_cross_run_index_marks_only_newest_valid_lane_active(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
        ],
    )

    harness.evaluate(run_id="older", stage="screen", source_path=source_path)
    older_manifest_path = tmp_path / "artifacts" / "older" / "run.json"
    older_manifest = json.loads(older_manifest_path.read_text())
    older_manifest["created_at"] = "2026-04-11T16:52:11+00:00"
    older_manifest_path.write_text(json.dumps(older_manifest, indent=2, sort_keys=True))

    harness.evaluate(run_id="newer", stage="screen", source_path=source_path)
    newer_manifest_path = tmp_path / "artifacts" / "newer" / "run.json"
    newer_manifest = json.loads(newer_manifest_path.read_text())
    newer_manifest["created_at"] = "2026-04-12T18:30:59+00:00"
    newer_manifest_path.write_text(json.dumps(newer_manifest, indent=2, sort_keys=True))

    harness._write_cross_run_index()

    index_payload = json.loads((tmp_path / "index.json").read_text())
    statuses = {
        run["run_id"]: {"status": run["status"], "notes": run["notes"]}
        for run in index_payload["hill_climb_runs"]
    }

    assert statuses["newer"]["status"] == "active"
    assert statuses["older"]["status"] == "historical"
    assert statuses["older"]["notes"][0] == "superseded by retained lane newer"


def test_cross_run_index_marks_closed_latest_lane_historical(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[4.0, 4.0, 4.0, 4.0]),
        ],
    )

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    source_path.write_text("// closed batch")
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    index_payload = json.loads((tmp_path / "index.json").read_text())
    run_entry = index_payload["hill_climb_runs"][0]

    assert run_entry["run_id"] == "mar26"
    assert run_entry["status"] == "historical"
    assert run_entry["notes"] == [
        "batch closed with no queued next hypothesis; seed a fresh run_id for the next branch"
    ]


def test_cross_run_index_demotes_older_active_lane_when_latest_history_is_closed(
    tmp_path,
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
            _make_match_result(mean_edges=[4.0, 4.0, 4.0, 4.0]),
        ],
    )

    harness.evaluate(run_id="older", stage="screen", source_path=source_path)
    older_manifest_path = tmp_path / "artifacts" / "older" / "run.json"
    older_manifest = json.loads(older_manifest_path.read_text())
    older_manifest["created_at"] = "2026-04-11T16:52:11+00:00"
    older_manifest_path.write_text(json.dumps(older_manifest, indent=2, sort_keys=True))
    harness.upsert_hypothesis(
        run_id="older",
        hypothesis_id="next-idea",
        title="Next idea",
        rationale="Keep the older lane notionally active.",
        expected_effect="None",
        mutation_family="older-family",
        status="queued",
        **_structural_hypothesis_kwargs(),
    )
    harness.update_run_state(
        run_id="older",
        next_hypothesis_id="next-idea",
        next_hypothesis_id_set=True,
    )

    source_path.write_text("// latest seed")
    harness.evaluate(run_id="latest", stage="screen", source_path=source_path)
    latest_manifest_path = tmp_path / "artifacts" / "latest" / "run.json"
    latest_manifest = json.loads(latest_manifest_path.read_text())
    latest_manifest["created_at"] = "2026-04-12T18:30:59+00:00"
    latest_manifest_path.write_text(
        json.dumps(latest_manifest, indent=2, sort_keys=True)
    )
    source_path.write_text("// latest closed")
    harness.evaluate(run_id="latest", stage="screen", source_path=source_path)

    index_payload = json.loads((tmp_path / "index.json").read_text())
    statuses = {entry["run_id"]: entry for entry in index_payload["hill_climb_runs"]}

    assert statuses["latest"]["status"] == "historical"
    assert statuses["older"]["status"] == "historical"
    assert statuses["older"]["notes"][0] == (
        "superseded by latest retained history latest"
    )


def test_prescreen_stage_rejects_spiky_or_arb_leaky_candidates(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    result = _make_match_result(mean_edges=[1.0, 1.0, 1.0, 1.0])
    for simulation in result.simulation_results:
        simulation.arb_edge["submission"] = -5.0
        simulation.retail_edge["submission"] = 10.0
        simulation.max_fee_jump["submission"] = 0.02

    harness = _build_test_harness(tmp_path, match_results=[result])
    summary = harness.evaluate(
        run_id="mar26",
        stage="prescreen",
        source_path=source_path,
        label="risky-pivot",
    )

    assert summary["status"] == "discard"
    assert summary["scorecard"]["gate"]["passed"] is False
    assert any(
        "max_fee_jump" in failure
        for failure in summary["scorecard"]["gate"]["failures"]
    )


def test_evaluate_discards_small_noisy_improvement(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[0.0, 5.0, 10.0, 5.0]),
            _make_match_result(mean_edges=[0.5, 5.5, 10.5, 5.5]),
        ],
    )

    first = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        label="baseline",
    )
    source_path.write_text("// candidate noisy uplift")
    second = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        label="small-noisy-uplift",
    )

    assert first["status"] == "seed"
    assert second["status"] == "discard"
    assert second["delta_vs_incumbent"] == pytest.approx(0.5)
    assert second["selection"]["promotion_margin"] == pytest.approx(2.5)
    assert "did not clear promotion margin" in second["selection"]["rationale"]


def test_pull_best_restores_incumbent_snapshot(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// seed")

    harness = _build_test_harness(tmp_path)

    summary = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    restored_path = tmp_path / "restored" / "Strategy.sol"
    source_path.write_text("// changed")

    destination = harness.pull_best(
        run_id="mar26",
        stage="screen",
        destination=restored_path,
    )

    assert destination == restored_path
    assert restored_path.read_text() == Path(summary["snapshot_path"]).read_text()


def test_evaluate_rejects_alternate_source_path_for_existing_run(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// active")
    alternate_path = tmp_path / "Alternate.sol"
    alternate_path.write_text("// alternate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
        ],
    )

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    with pytest.raises(HillClimbHarnessError, match="active strategy path"):
        harness.evaluate(run_id="mar26", stage="screen", source_path=alternate_path)


def test_hill_climb_eval_command_rejects_nondefault_active_path(capsys):
    args = argparse.Namespace(
        strategy="contracts/src/StarterStrategy.sol",
        run_id="mar26",
        stage="screen",
        artifact_root="artifacts/hill_climb",
        label=None,
        description=None,
    )

    exit_code = hill_climb_eval_command(args)

    assert exit_code == 1
    assert "contracts/src/Strategy.sol" in capsys.readouterr().out


def test_hill_climb_eval_command_rejects_dirty_protected_surface(
    tmp_path, monkeypatch, capsys
):
    repo_root, strategy_path, protected_path = _build_protected_repo(tmp_path)
    protected_path.write_text("BASELINE = 2\n")

    args = argparse.Namespace(
        strategy=str(strategy_path),
        run_id="mar26",
        stage="screen",
        artifact_root=str(repo_root / "artifacts"),
        label=None,
        description=None,
    )

    class _UnexpectedHarness:
        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs

        def evaluate(self, **kwargs):
            del kwargs
            raise AssertionError(
                "evaluate should not run when protected mechanics are dirty"
            )

    monkeypatch.setattr(
        "amm_competition.cli._validate_active_hill_climb_strategy_path",
        lambda path: path,
    )
    monkeypatch.setattr(
        "amm_competition.cli.ProtectedSurfaceChecker.discover",
        lambda: ProtectedSurfaceChecker(repo_root=repo_root),
    )
    monkeypatch.setattr("amm_competition.cli.HillClimbHarness", _UnexpectedHarness)

    exit_code = hill_climb_eval_command(args)

    assert exit_code == 1
    output = capsys.readouterr().out
    assert "Hill-climb evaluation failed:" in output
    assert "amm_competition/competition/config.py" in output


def test_hill_climb_eval_command_allows_dirty_protected_surface_with_override(
    tmp_path, monkeypatch, capsys
):
    repo_root, strategy_path, protected_path = _build_protected_repo(tmp_path)
    protected_path.write_text("BASELINE = 2\n")

    args = argparse.Namespace(
        strategy=str(strategy_path),
        run_id="mar26",
        stage="screen",
        artifact_root=str(repo_root / "artifacts"),
        label="override-check",
        description=None,
    )

    class _StubHarness:
        def __init__(self, *args, **kwargs) -> None:
            del args, kwargs

        def evaluate(self, **kwargs):
            del kwargs
            return {
                "run_id": "mar26",
                "eval_id": "screen_0001",
                "stage": "screen",
                "status": "seed",
                "mean_edge": 1.25,
                "snapshot_path": str(strategy_path),
            }

    monkeypatch.setenv("ALLOW_COMPETITION_MECHANICS_EDIT", "1")
    monkeypatch.setattr(
        "amm_competition.cli._validate_active_hill_climb_strategy_path",
        lambda path: path,
    )
    monkeypatch.setattr(
        "amm_competition.cli.ProtectedSurfaceChecker.discover",
        lambda: ProtectedSurfaceChecker(repo_root=repo_root),
    )
    monkeypatch.setattr("amm_competition.cli.HillClimbHarness", _StubHarness)

    exit_code = hill_climb_eval_command(args)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Run: mar26" in output
    assert "Eval: screen_0001" in output


def test_get_stage_status_rejects_changed_protected_surface_fingerprint_for_existing_run(
    tmp_path,
):
    repo_root, strategy_path, protected_path = _build_protected_repo(tmp_path)
    harness = HillClimbHarness(
        artifact_root=repo_root / "artifacts",
        n_workers=1,
        strategy_loader=cast(Any, _FixedStrategyLoader()),
        baseline_loader=lambda: object(),
        stage_runner_factory=_SequentialRunnerFactory(
            [_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])]
        ),
        protected_surface_checker=ProtectedSurfaceChecker(repo_root=repo_root),
    )

    harness.evaluate(run_id="mar26", stage="screen", source_path=strategy_path)
    protected_path.write_text("BASELINE = 3\n")

    with pytest.raises(
        HillClimbHarnessError,
        match="pinned to a different protected competition mechanics surface",
    ):
        harness.get_stage_status(run_id="mar26", stage="screen")


def test_status_and_summary_allow_read_only_analysis_on_protected_surface_drift(
    tmp_path, capsys
):
    repo_root, strategy_path, protected_path = _build_protected_repo(tmp_path)
    harness = HillClimbHarness(
        artifact_root=repo_root / "artifacts",
        n_workers=1,
        strategy_loader=cast(Any, _FixedStrategyLoader()),
        baseline_loader=lambda: object(),
        stage_runner_factory=_SequentialRunnerFactory(
            [_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])]
        ),
        protected_surface_checker=ProtectedSurfaceChecker(repo_root=repo_root),
    )

    harness.evaluate(run_id="mar26", stage="screen", source_path=strategy_path)
    protected_path.write_text("BASELINE = 3\n")

    status_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(repo_root / "artifacts"),
        stage="screen",
        read_only=True,
    )
    summarize_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(repo_root / "artifacts"),
        read_only=True,
    )

    assert hill_climb_status_command(status_args) == 0
    status_output = capsys.readouterr().out
    assert (
        "Warning: Run 'mar26' is pinned to a different protected competition mechanics surface"
        in status_output
    )

    assert hill_climb_summarize_run_command(summarize_args) == 0
    summarize_output = capsys.readouterr().out
    assert "Frontier Bank:" in summarize_output
    assert (
        "Warning: Run 'mar26' is pinned to a different protected competition mechanics surface"
        in summarize_output
    )


def test_get_stage_status_requires_existing_run(tmp_path):
    harness = HillClimbHarness(artifact_root=tmp_path / "artifacts", n_workers=1)
    with pytest.raises(HillClimbHarnessError, match="Unknown hill-climb run"):
        harness.get_stage_status(run_id="missing", stage="screen")


def test_get_stage_status_rejects_obsolete_continuity_file(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(tmp_path)

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    run_dir = tmp_path / "artifacts" / "mar26"
    (run_dir / LEGACY_NEXT_EVAL_ID_FILENAME).write_text("2\n")

    with pytest.raises(
        HillClimbHarnessError, match="obsolete continuity file"
    ) as excinfo:
        harness.get_stage_status(run_id="mar26", stage="screen")
    assert (
        "Do not hand-edit results.jsonl, results.tsv, state.json, or .next_eval_index"
        in str(excinfo.value)
    )
    assert "Quarantine the run directory and start a fresh run_id instead." in str(
        excinfo.value
    )


def test_get_stage_status_rejects_duplicate_eval_ids(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(tmp_path)

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    run_dir = tmp_path / "artifacts" / "mar26"
    results_jsonl = run_dir / "results.jsonl"
    payload = results_jsonl.read_text().splitlines()[0]
    results_jsonl.write_text(f"{payload}\n{payload}\n")
    results_tsv = run_dir / "results.tsv"
    lines = results_tsv.read_text().splitlines()
    results_tsv.write_text("\n".join([lines[0], lines[1], lines[1]]) + "\n")
    (run_dir / ".next_eval_index").write_text("3\n")

    with pytest.raises(HillClimbHarnessError, match="duplicate eval_id") as excinfo:
        harness.get_stage_status(run_id="mar26", stage="screen")
    assert (
        "Do not hand-edit results.jsonl, results.tsv, state.json, or .next_eval_index"
        in str(excinfo.value)
    )
    assert "Quarantine the run directory and start a fresh run_id instead." in str(
        excinfo.value
    )


def test_get_stage_status_rejects_malformed_results_jsonl(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(tmp_path)

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    run_dir = tmp_path / "artifacts" / "mar26"
    (run_dir / "results.jsonl").write_text("{not valid json}\n")

    with pytest.raises(HillClimbHarnessError, match="Invalid JSON in .*results.jsonl"):
        harness.get_stage_status(run_id="mar26", stage="screen")


def test_get_stage_status_rejects_malformed_incumbent_json(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(tmp_path)

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    run_dir = tmp_path / "artifacts" / "mar26"
    (run_dir / "incumbents" / "screen.json").write_text("{not valid json}\n")

    with pytest.raises(HillClimbHarnessError, match="Invalid JSON in .*screen.json"):
        harness.get_stage_status(run_id="mar26", stage="screen")


def test_parallel_evaluations_get_distinct_eval_ids(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    barrier = threading.Barrier(2)

    class _SynchronizedHarness(HillClimbHarness):
        def _ensure_run_dir(self, run_id, source_path, *, target_stage):
            run_dir = super()._ensure_run_dir(
                run_id, source_path, target_stage=target_stage
            )
            barrier.wait()
            return run_dir

    harness = _SynchronizedHarness(
        artifact_root=tmp_path / "artifacts",
        n_workers=1,
        strategy_loader=cast(Any, _FixedStrategyLoader()),
        baseline_loader=lambda: object(),
        stage_runner_factory=_SequentialRunnerFactory(
            [
                _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
                _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            ]
        ),
    )

    summaries: list[dict] = []
    errors: list[BaseException] = []

    def run_eval(label: str) -> None:
        try:
            summaries.append(
                harness.evaluate(
                    run_id="mar26",
                    stage="smoke",
                    source_path=source_path,
                    label=label,
                    replay_reason="parallel identical-source replay for eval-id reservation",
                )
            )
        except BaseException as exc:  # pragma: no cover - test should not fail here
            errors.append(exc)

    first = threading.Thread(target=run_eval, args=("first",))
    second = threading.Thread(target=run_eval, args=("second",))
    first.start()
    second.start()
    first.join()
    second.join()

    assert errors == []
    assert len(summaries) == 2
    assert {summary["eval_id"] for summary in summaries} == {"smoke_0001", "smoke_0002"}

    results = (
        (tmp_path / "artifacts" / "mar26" / "results.tsv").read_text().splitlines()
    )
    assert len(results) == 3
    assert results[1].startswith("smoke_0001\t")
    assert results[2].startswith("smoke_0002\t")


def test_off_target_eval_preserves_current_target_stage(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[4.0, 4.0, 4.0, 4.0]),
        ],
    )

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    harness.evaluate(run_id="mar26", stage="smoke", source_path=source_path)

    state = _load_json(tmp_path / "artifacts" / "mar26" / "state.json")
    assert state["current_target_stage"] == "screen"


def test_set_state_updates_loop_metadata_and_status_reports_guidance(
    tmp_path, capsys, monkeypatch
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[4.0, 4.0, 4.0, 4.0]),
            _make_match_result(mean_edges=[3.0, 3.0, 3.0, 3.0]),
            _make_match_result(mean_edges=[2.0, 2.0, 2.0, 2.0]),
            _make_match_result(mean_edges=[1.0, 1.0, 1.0, 1.0]),
            _make_match_result(mean_edges=[0.0, 0.0, 0.0, 0.0]),
        ],
    )

    for idx in range(6):
        source_path.write_text(f"// candidate {idx}")
        harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    monkeypatch.setattr(
        "amm_competition.hill_climb.harness.ProtectedSurfaceChecker.discover",
        lambda: _NoopProtectedSurfaceChecker(),
    )
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="lower-ask-sooner",
        title="Lower the ask fee sooner",
        rationale="Shorten the toxic widening lag after small clustered buys",
        expected_effect="Improve screen mean_edge without broad carry drag",
        mutation_family="timing-overlay",
        status="queued",
        **_structural_hypothesis_kwargs(),
    )

    set_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        current_target_stage="screen",
        next_hypothesis_id="lower-ask-sooner",
        next_hypothesis_note="Lower the ask fee sooner",
        clear_next_hypothesis=False,
        run_mode="background",
        refine_after=4,
        pivot_after=5,
        stop_after=8,
        breakout_stage="screen",
        breakout_threshold=6.0,
        clear_breakout_goal=False,
    )
    assert hill_climb_set_state_command(set_args) == 0

    state = _load_json(tmp_path / "artifacts" / "mar26" / "state.json")
    assert state["current_target_stage"] == "screen"
    assert state["next_hypothesis_id"] == "lower-ask-sooner"
    assert state["next_hypothesis_note"] == "Lower the ask fee sooner"
    assert state["run_mode"] == "background"
    assert state["stop_rules"] == {
        "refine_after_non_improving_iterations": 4,
        "pivot_after_non_improving_iterations": 5,
        "stop_after_non_improving_iterations": 8,
    }
    assert state["outcome_gate"] == {
        "stage": "screen",
        "minimum_mean_edge": 6.0,
    }

    status_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        stage="screen",
    )
    assert hill_climb_status_command(status_args) == 0
    output = capsys.readouterr().out
    assert "Current Target Stage: screen" in output
    assert "Run Mode: background" in output
    assert "Next Hypothesis: lower-ask-sooner (Lower the ask fee sooner)" in output
    assert (
        "Outcome Gate: pending (screen incumbent 5.000000 is below target 6.000000)"
        in output
    )
    assert "Target-Stage Non-Improving Streak: 5" in output
    assert "Stop-Rule Guidance: pivot now" in output


def test_set_hypothesis_supports_structured_experiment_fields(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")
    harness = _build_test_harness(tmp_path)
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    payload = harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="anti-arb-pivot",
        title="Anti-arb pivot",
        rationale="Tighten toxic-flow discrimination before lowering fees",
        expected_effect="Reduce arb leakage in calm states",
        mutation_family="anti-arb",
        target_metrics={"arb_edge": -20.0},
        hard_guardrails={"max_fee_jump": 0.005},
        expected_failure_mode="arb_leak_regression",
        novelty_coordinates={"intent": "anti-arb"},
        synthesis_eligible=False,
        nearest_prior_failures=["timing-overlay"],
        nearest_prior_successes=["screen-seed"],
        **_structural_hypothesis_kwargs(
            primary_layer_changed="risk_budget",
            layer_held_fixed="opportunity_budget",
            quote_topology="hazard-gated-release",
        ),
    )

    assert payload["target_metrics"] == {"arb_edge": -20.0}
    assert payload["hard_guardrails"] == {"max_fee_jump": 0.005}
    assert payload["expected_failure_mode"] == "arb_leak_regression"
    assert payload["novelty_coordinates"] == {"intent": "anti-arb"}
    assert payload["synthesis_eligible"] is False
    assert payload["nearest_prior_failures"] == ["timing-overlay"]
    assert payload["nearest_prior_successes"] == ["screen-seed"]
    assert payload["primary_layer_changed"] == "risk_budget"
    assert payload["quote_topology"] == "hazard-gated-release"


def test_set_hypothesis_requires_structural_contract_for_new_hypotheses(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")
    harness = _build_test_harness(tmp_path)
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    with pytest.raises(HillClimbHarnessError, match="New hypotheses require batch_id"):
        harness.upsert_hypothesis(
            run_id="mar26",
            hypothesis_id="missing-structure",
            title="Missing structure",
            rationale="Exercise new contract enforcement",
            expected_effect="None",
            mutation_family="validation",
        )


def test_set_hypothesis_rejects_unknown_failure_mode_and_nonserializable_novelty(
    tmp_path,
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")
    harness = _build_test_harness(tmp_path)
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    with pytest.raises(HillClimbHarnessError, match="unknown expected_failure_mode"):
        harness.upsert_hypothesis(
            run_id="mar26",
            hypothesis_id="bad-failure-mode",
            title="Bad failure mode",
            rationale="Exercise validation",
            expected_effect="None",
            mutation_family="validation",
            expected_failure_mode="made_up_mode",
            **_structural_hypothesis_kwargs(),
        )

    with pytest.raises(HillClimbHarnessError, match="JSON-serializable object"):
        harness.upsert_hypothesis(
            run_id="mar26",
            hypothesis_id="bad-novelty",
            title="Bad novelty",
            rationale="Exercise validation",
            expected_effect="None",
            mutation_family="validation",
            novelty_coordinates={"bad": {1, 2, 3}},
            **_structural_hypothesis_kwargs(),
        )


def test_set_hypothesis_rejects_unknown_metric_keys(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")
    harness = _build_test_harness(tmp_path)
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    with pytest.raises(HillClimbHarnessError, match="Unknown target_metrics metric"):
        harness.upsert_hypothesis(
            run_id="mar26",
            hypothesis_id="bad-metric",
            title="Bad metric",
            rationale="Exercise metric validation",
            expected_effect="None",
            mutation_family="validation",
            target_metrics={"made_up_metric": 1.0},
            **_structural_hypothesis_kwargs(),
        )


def test_set_hypothesis_command_parses_structured_experiment_fields(
    tmp_path, capsys, monkeypatch
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")
    harness = _build_test_harness(tmp_path)
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    monkeypatch.setattr(
        "amm_competition.hill_climb.harness.ProtectedSurfaceChecker.discover",
        lambda: _NoopProtectedSurfaceChecker(),
    )

    args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        hypothesis_id="cli-shaped",
        title="CLI shaped",
        rationale="Exercise parser wiring",
        expected_effect="Keep the command path covered",
        mutation_family="cli-test",
        status="queued",
        batch_id="batch-001",
        parent_hypothesis_id=None,
        seed_eval_id=None,
        research_refs=["docs/plans/active/apr01-screen420-2134.md"],
        target_metrics=["arb_edge=-20"],
        hard_guardrails=["max_fee_jump=0.005"],
        expected_failure_mode="arb_leak_regression",
        actual_failure_mode=None,
        novelty_coordinates='{"intent":"parser"}',
        synthesis_eligible=False,
        nearest_prior_failures=["timing-overlay"],
        nearest_prior_successes=["screen-seed"],
        primary_layer_changed="state",
        layer_held_fixed="quote_map",
        hidden_coupling_removed="Anchor estimation and cheap release share the same trigger.",
        why_not_coefficient_retune="The branch changes the gating contract instead of shrinking overlays.",
        expected_win_condition="Improve calm quoting only when anchor confidence recovers.",
        expected_failure_signature="Cheap mode turns on too early and recreates arb leakage.",
        quote_topology="anchor-gated-router",
        is_topology_branch=True,
    )

    assert hill_climb_set_hypothesis_command(args) == 0
    output = capsys.readouterr().out
    assert "Hypothesis: cli-shaped" in output
    payload = harness.get_hypothesis(run_id="mar26", hypothesis_id="cli-shaped")
    assert payload["target_metrics"] == {"arb_edge": -20.0}
    assert payload["hard_guardrails"] == {"max_fee_jump": 0.005}
    assert payload["novelty_coordinates"] == {"intent": "parser"}
    assert payload["synthesis_eligible"] is False
    assert payload["batch_id"] == "batch-001"
    assert payload["is_topology_branch"] is True


def test_successful_eval_does_not_overwrite_actual_failure_mode(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
        ],
    )
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="protect-failure-mode",
        title="Protect failure mode",
        rationale="Do not clobber recorded failure labels on success",
        expected_effect="Keep taxonomy stable",
        mutation_family="validation",
        actual_failure_mode="arb_leak_regression",
        **_structural_hypothesis_kwargs(),
    )

    source_path.write_text("// improved")
    harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        hypothesis_id="protect-failure-mode",
    )

    payload = harness.get_hypothesis(
        run_id="mar26", hypothesis_id="protect-failure-mode"
    )
    assert payload["actual_failure_mode"] == "arb_leak_regression"


def test_set_state_rejects_partial_breakout_goal_configuration(
    tmp_path, capsys, monkeypatch
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(tmp_path)
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    monkeypatch.setattr(
        "amm_competition.hill_climb.harness.ProtectedSurfaceChecker.discover",
        lambda: _NoopProtectedSurfaceChecker(),
    )

    set_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        current_target_stage=None,
        next_hypothesis_id=None,
        next_hypothesis_note=None,
        clear_next_hypothesis=False,
        run_mode=None,
        refine_after=None,
        pivot_after=None,
        stop_after=None,
        breakout_stage="screen",
        breakout_threshold=None,
        clear_breakout_goal=False,
    )

    assert hill_climb_set_state_command(set_args) == 1
    assert (
        "choose both --breakout-stage and --breakout-threshold"
        in capsys.readouterr().out
    )


def test_get_run_state_rejects_missing_outcome_gate_field(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(tmp_path)
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    state_path = tmp_path / "artifacts" / "mar26" / "state.json"
    state = _load_json(state_path)
    del state["outcome_gate"]
    state_path.write_text(json.dumps(state))

    with pytest.raises(
        HillClimbHarnessError, match="state is missing required fields: outcome_gate"
    ):
        harness.get_run_state(run_id="mar26")


def test_get_run_state_rejects_out_of_order_stop_rules(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// candidate")

    harness = _build_test_harness(tmp_path)
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    state_path = tmp_path / "artifacts" / "mar26" / "state.json"
    state = _load_json(state_path)
    state["stop_rules"] = {
        "refine_after_non_improving_iterations": 6,
        "pivot_after_non_improving_iterations": 5,
        "stop_after_non_improving_iterations": 8,
    }
    state_path.write_text(json.dumps(state))

    with pytest.raises(
        HillClimbHarnessError, match="stop_rules must satisfy refine <= pivot <= stop"
    ):
        harness.get_run_state(run_id="mar26")


def test_hill_climb_history_and_lookup_commands_surface_agent_facing_read_models(
    tmp_path, capsys, monkeypatch
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// baseline")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
        ],
    )
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="timing-overlay",
        title="Timing overlay",
        rationale="Shorten widening lag",
        expected_effect="Lift screen edge",
        mutation_family="timing-overlay",
        status="queued",
        research_refs=["docs/plans/active/apr01-screen420-2134.md"],
        **_structural_hypothesis_kwargs(),
    )
    monkeypatch.setattr(
        "amm_competition.hill_climb.harness.ProtectedSurfaceChecker.discover",
        lambda: _NoopProtectedSurfaceChecker(),
    )
    source_path.write_text("// mutated")
    harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        hypothesis_id="timing-overlay",
        parent_eval_id="screen_0001",
        change_summary="Shorten widening lag",
        research_refs=["artifacts/research/run-a/memo.md"],
    )

    set_hypothesis_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        hypothesis_id="timing-overlay",
        title=None,
        rationale=None,
        expected_effect=None,
        mutation_family=None,
        status="completed",
        parent_hypothesis_id=None,
        seed_eval_id=None,
        research_refs=[],
    )
    assert hill_climb_set_hypothesis_command(set_hypothesis_args) == 0
    assert "Hypothesis: timing-overlay" in capsys.readouterr().out

    history_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
    )
    assert hill_climb_history_command(history_args) == 0
    history_output = capsys.readouterr().out
    assert "eval_id\tstage\tstatus" in history_output
    assert (
        "screen_0002\tscreen\tkeep\t6.000000\ttiming-overlay\tscreen_0001"
        in history_output
    )

    show_eval_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        eval_id="screen_0002",
    )
    assert hill_climb_show_eval_command(show_eval_args) == 0
    show_eval_output = capsys.readouterr().out
    assert "Hypothesis: timing-overlay" in show_eval_output
    assert "Parent Eval: screen_0001" in show_eval_output
    assert "Change Summary: Shorten widening lag" in show_eval_output

    show_hypothesis_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        hypothesis_id="timing-overlay",
    )
    assert hill_climb_show_hypothesis_command(show_hypothesis_args) == 0
    show_hypothesis_output = capsys.readouterr().out
    assert "Hypothesis: timing-overlay" in show_hypothesis_output
    assert "Batch: batch-001" in show_hypothesis_output
    assert "Seed Eval: screen_0002" in show_hypothesis_output
    assert "Eval IDs: screen_0002" in show_hypothesis_output
    assert "Primary Layer Changed: risk_budget" in show_hypothesis_output
    assert "Quote Topology: split-budget" in show_hypothesis_output

    summarize_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
    )
    assert hill_climb_summarize_run_command(summarize_args) == 0
    summarize_output = capsys.readouterr().out
    assert "Incumbent Chain:" in summarize_output
    assert "screen_0002 screen keep 6.000000" in summarize_output
    assert (
        "Decomposition Gaps: state, risk_budget, opportunity_budget, quote_map"
        in summarize_output
    )
    assert (
        "Batch Diversity: 0 primary layers, topology branch missing" in summarize_output
    )


def test_analyze_run_and_compare_profiles_commands_surface_frontier_and_profile_deltas(
    tmp_path, capsys, monkeypatch
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// baseline")

    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
        ],
    )
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    source_path.write_text("// improved")
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    monkeypatch.setattr(
        "amm_competition.hill_climb.harness.ProtectedSurfaceChecker.discover",
        lambda: _NoopProtectedSurfaceChecker(),
    )

    analyze_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        read_only=False,
        json=False,
    )
    assert hill_climb_analyze_run_command(analyze_args) == 0
    analyze_output = capsys.readouterr().out
    assert (
        "Decomposition Gaps: state, risk_budget, opportunity_budget, quote_map"
        in analyze_output
    )
    assert (
        "Batch Diversity: 0 primary layers, topology branch missing" in analyze_output
    )
    assert "Best Raw Frontier:" in analyze_output
    assert "screen_0002 screen 6.000000" in analyze_output
    assert (
        "Portfolio Gaps: anti_arb, weak_slice, fee_discipline, structural_pivot"
        in analyze_output
    )

    compare_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        stage="screen",
        baseline_eval_id="screen_0001",
        candidate_eval_id="screen_0002",
        anchor_eval_id="screen_0001",
        baseline_source=None,
        candidate_source=None,
        anchor_source=None,
        read_only=False,
        json=False,
    )
    assert hill_climb_compare_profiles_command(compare_args) == 0
    compare_output = capsys.readouterr().out
    assert "Baseline: screen_0001" in compare_output
    assert "Candidate vs Baseline:" in compare_output
    assert "mean_edge: 1.000000" in compare_output
    assert "Baseline vs Anchor:" in compare_output


def test_compare_profiles_command_requires_run_id_for_stored_eval_ids(tmp_path, capsys):
    args = argparse.Namespace(
        run_id=None,
        artifact_root=str(tmp_path / "artifacts"),
        stage="screen",
        baseline_eval_id="screen_0001",
        candidate_eval_id="screen_0002",
        anchor_eval_id=None,
        baseline_source=None,
        candidate_source=None,
        anchor_source=None,
        read_only=False,
        json=False,
    )

    assert hill_climb_compare_profiles_command(args) == 1
    assert (
        "--run-id is required when comparing stored eval ids" in capsys.readouterr().out
    )


def test_analyze_run_command_json_surfaces_planning_payload(
    tmp_path, capsys, monkeypatch
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// baseline")
    harness = _build_test_harness(
        tmp_path,
        match_results=[_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])],
    )
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    monkeypatch.setattr(
        "amm_competition.hill_climb.harness.ProtectedSurfaceChecker.discover",
        lambda: _NoopProtectedSurfaceChecker(),
    )

    args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        read_only=False,
        json=True,
    )

    assert hill_climb_analyze_run_command(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["portfolio_gaps"] == [
        "anti_arb",
        "weak_slice",
        "fee_discipline",
        "structural_pivot",
    ]
    assert payload["decomposition_gaps"] == [
        "state",
        "risk_budget",
        "opportunity_budget",
        "quote_map",
    ]
    assert payload["batch_diversity"]["distinct_primary_layer_count"] == 0
    assert payload["batch_diversity"]["has_topology_branch"] is False
    assert payload["recommended_next_batch"][0]["intent"] == "local_refine"


def test_analyze_run_treats_three_layer_open_batch_as_contract_complete(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// baseline")
    harness = _build_test_harness(
        tmp_path,
        match_results=[_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])],
    )
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="state-branch",
        title="State branch",
        rationale="Split anchor estimation from release timing.",
        expected_effect="Improve calm repricing without broad fee cuts.",
        mutation_family="state-branch",
        status="queued",
        **_structural_hypothesis_kwargs(
            primary_layer_changed="state",
            layer_held_fixed="quote_map",
            quote_topology="anchor-gated",
            is_topology_branch=False,
        ),
    )
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="risk-branch",
        title="Risk branch",
        rationale="Separate shared spread from one-sided protection.",
        expected_effect="Reduce hidden cheap-mode coupling in dangerous states.",
        mutation_family="risk-branch",
        status="queued",
        **_structural_hypothesis_kwargs(
            primary_layer_changed="risk_budget",
            layer_held_fixed="state",
            quote_topology="hazard-split",
            is_topology_branch=False,
        ),
    )
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="quote-map-branch",
        title="Quote map branch",
        rationale="Change quote assembly without retuning the incumbent spine.",
        expected_effect="Test a true topology pivot with bounded competitive spend.",
        mutation_family="quote-map-branch",
        status="queued",
        **_structural_hypothesis_kwargs(
            primary_layer_changed="quote_map",
            layer_held_fixed="risk_budget",
            quote_topology="router-pivot",
            is_topology_branch=True,
        ),
    )

    payload = harness.analyze_run(run_id="mar26")
    assert payload["decomposition_gaps"] == ["opportunity_budget"]
    assert payload["batch_diversity"]["distinct_primary_layer_count"] == 3
    assert payload["batch_diversity"]["has_topology_branch"] is True
    assert payload["structural_recommendations"] == [
        {
            "kind": "batch_contract",
            "covered": True,
            "reason": "Open hypotheses satisfy the minimum layer and topology diversity contract.",
        }
    ]


def test_analyze_run_scopes_diversity_to_latest_batch(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// baseline")
    harness = _build_test_harness(
        tmp_path,
        match_results=[_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])],
    )
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="older-state",
        title="Older state",
        rationale="Older batch state branch.",
        expected_effect="Legacy open branch.",
        mutation_family="older",
        status="queued",
        **_structural_hypothesis_kwargs(
            batch_id="batch-001",
            primary_layer_changed="state",
            layer_held_fixed="quote_map",
            quote_topology="older-anchor",
            is_topology_branch=False,
        ),
    )
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="older-risk",
        title="Older risk",
        rationale="Older batch risk branch.",
        expected_effect="Legacy open branch.",
        mutation_family="older",
        status="queued",
        **_structural_hypothesis_kwargs(
            batch_id="batch-001",
            primary_layer_changed="risk_budget",
            layer_held_fixed="state",
            quote_topology="older-hazard",
            is_topology_branch=False,
        ),
    )
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="older-quote",
        title="Older quote map",
        rationale="Older batch topology branch.",
        expected_effect="Legacy open branch.",
        mutation_family="older",
        status="queued",
        **_structural_hypothesis_kwargs(
            batch_id="batch-001",
            primary_layer_changed="quote_map",
            layer_held_fixed="risk_budget",
            quote_topology="older-router",
            is_topology_branch=True,
        ),
    )
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="latest-risk",
        title="Latest risk",
        rationale="Newest batch is intentionally narrow.",
        expected_effect="Surface decomposition-gap enforcement.",
        mutation_family="latest",
        status="queued",
        **_structural_hypothesis_kwargs(
            batch_id="batch-002",
            primary_layer_changed="risk_budget",
            layer_held_fixed="quote_map",
            quote_topology="latest-hazard",
            is_topology_branch=False,
        ),
    )

    payload = harness.analyze_run(run_id="mar26")
    assert payload["batch_diversity"]["batch_id"] == "batch-002"
    assert payload["batch_diversity"]["selection_mode"] == "explicit_batch_id"
    assert payload["batch_diversity"]["open_hypothesis_ids"] == ["latest-risk"]
    assert payload["decomposition_gaps"] == ["state", "opportunity_budget", "quote_map"]
    assert payload["batch_diversity"]["distinct_primary_layer_count"] == 1
    assert payload["batch_diversity"]["has_topology_branch"] is False
    assert payload["structural_recommendations"] == [
        {
            "kind": "decomposition_gap",
            "covered": False,
            "reason": (
                "Open batch does not yet cover three distinct decomposition targets; "
                "next additions should include: state, opportunity_budget, quote_map."
            ),
        },
        {
            "kind": "topology_branch",
            "covered": False,
            "reason": (
                "Reserve at least one branch that changes how the quote is assembled, "
                "not just how incumbent terms are tuned."
            ),
        },
    ]


def test_analyze_run_keeps_same_spine_failure_signal_beyond_last_five_results(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[10.0, 10.0, 10.0, 10.0]),
            _make_match_result(mean_edges=[4.0, 4.0, 4.0, 4.0]),
            _make_match_result(mean_edges=[4.1, 4.1, 4.1, 4.1]),
            _make_match_result(mean_edges=[4.2, 4.2, 4.2, 4.2]),
            _make_match_result(mean_edges=[4.3, 4.3, 4.3, 4.3]),
            _make_match_result(mean_edges=[4.4, 4.4, 4.4, 4.4]),
            _make_match_result(mean_edges=[4.5, 4.5, 4.5, 4.5]),
            _make_match_result(mean_edges=[4.6, 4.6, 4.6, 4.6]),
        ],
    )
    source_path.write_text("// baseline")
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    failure_specs = [
        ("same-spine-a", _structural_hypothesis_kwargs(batch_id="batch-001")),
        ("same-spine-b", _structural_hypothesis_kwargs(batch_id="batch-001")),
        (
            "other-1",
            _structural_hypothesis_kwargs(
                batch_id="batch-001",
                primary_layer_changed="state",
                layer_held_fixed="quote_map",
                quote_topology="anchor-1",
            ),
        ),
        (
            "other-2",
            _structural_hypothesis_kwargs(
                batch_id="batch-001",
                primary_layer_changed="state",
                layer_held_fixed="quote_map",
                quote_topology="anchor-2",
            ),
        ),
        (
            "other-3",
            _structural_hypothesis_kwargs(
                batch_id="batch-001",
                primary_layer_changed="quote_map",
                layer_held_fixed="risk_budget",
                quote_topology="router-1",
            ),
        ),
        (
            "other-4",
            _structural_hypothesis_kwargs(
                batch_id="batch-001",
                primary_layer_changed="quote_map",
                layer_held_fixed="risk_budget",
                quote_topology="router-2",
            ),
        ),
        (
            "other-5",
            _structural_hypothesis_kwargs(
                batch_id="batch-001",
                primary_layer_changed="opportunity_budget",
                layer_held_fixed="state",
                quote_topology="release-1",
            ),
        ),
    ]
    for index, (hypothesis_id, kwargs) in enumerate(failure_specs, start=1):
        harness.upsert_hypothesis(
            run_id="mar26",
            hypothesis_id=hypothesis_id,
            title=f"Hypothesis {index}",
            rationale="Create failure history.",
            expected_effect="None",
            mutation_family="failure-history",
            status="queued",
            **kwargs,
        )
        source_path.write_text(f"// variant {index}")
        harness.evaluate(
            run_id="mar26",
            stage="screen",
            source_path=source_path,
            hypothesis_id=hypothesis_id,
        )

    payload = harness.analyze_run(run_id="mar26")
    assert payload["batch_diversity"]["force_layer_pivot"] is True
    assert payload["batch_diversity"]["same_spine_failure_groups"] == {
        "risk_budget->quote_map:split-budget": ["same-spine-a", "same-spine-b"]
    }
    assert payload["structural_recommendations"][0] == {
        "kind": "layer_pivot",
        "covered": False,
        "reason": (
            "Recent survivors or failures show same-spine replay pressure; "
            "switch primary layer before another coefficient retune."
        ),
    }


def test_analyze_run_builds_research_notebook_and_search_risk_files(tmp_path):
    source_path = tmp_path / "Strategy.sol"
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
            _make_match_result(mean_edges=[4.0, 4.0, 4.0, 4.0]),
            _make_match_result(mean_edges=[4.1, 4.1, 4.1, 4.1]),
        ],
    )
    source_path.write_text("// baseline")
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="winner",
        title="Winner",
        rationale="Prove a successful family is retained in the notebook.",
        expected_effect="Lift screen mean_edge.",
        mutation_family="winner-family",
        status="queued",
        **_structural_hypothesis_kwargs(
            primary_layer_changed="state",
            layer_held_fixed="quote_map",
            quote_topology="winner-topology",
        ),
    )
    source_path.write_text("// winner")
    harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        hypothesis_id="winner",
    )
    harness.upsert_hypothesis(
        run_id="mar26",
        hypothesis_id="dead-end",
        title="Dead end",
        rationale="Create a family with repeated discards.",
        expected_effect="None",
        mutation_family="dead-family",
        status="queued",
        **_structural_hypothesis_kwargs(
            primary_layer_changed="quote_map",
            layer_held_fixed="risk_budget",
            quote_topology="dead-topology",
        ),
    )
    source_path.write_text("// dead-end a")
    harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        hypothesis_id="dead-end",
    )
    source_path.write_text("// dead-end b")
    harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        hypothesis_id="dead-end",
    )

    payload = harness.analyze_run(run_id="mar26")
    winner_family = payload["family_scoreboard"]["winner-family"]
    dead_family = payload["family_scoreboard"]["dead-family"]
    assert winner_family["survivor_count"] == 1
    assert winner_family["risk_label"] == "low"
    assert dead_family["attempt_count"] == 2
    assert dead_family["dead_end"] is True
    assert dead_family["risk_label"] == "high"
    assert payload["layer_scoreboard"]["state"]["survivor_count"] == 1
    assert payload["layer_scoreboard"]["quote_map"]["attempt_count"] == 2
    assert payload["research_notebook"]["findings"] == [
        {
            "kind": "mutation_family",
            "subject": "winner-family",
            "note": (
                "winner-family survived 1/1 attempts; best eval "
                "screen_0002 reached mean_edge 6.000000."
            ),
        }
    ]
    assert payload["research_notebook"]["dead_ends"] == [
        {
            "kind": "mutation_family",
            "subject": "dead-family",
            "note": (
                "dead-family has no survivors across 2 attempts; "
                "latest status: discard."
            ),
        }
    ]

    run_dir = tmp_path / "artifacts" / "mar26" / "notebook"
    assert (
        "winner-family survived 1/1 attempts" in (run_dir / "findings.md").read_text()
    )
    assert (
        "dead-family has no survivors across 2 attempts"
        in (run_dir / "dead_ends.md").read_text()
    )
    search_risk = (run_dir / "search_risk.md").read_text()
    assert "dead-family [HIGH risk, fragility=1.00]" in search_risk
    assert "winner-family [LOW risk, fragility=0.00]" in search_risk


def test_compare_profiles_command_rejects_mixed_inputs_and_stage_mismatch(
    tmp_path, capsys, monkeypatch
):
    source_path = tmp_path / "Strategy.sol"
    source_path.write_text("// baseline")
    harness = _build_test_harness(
        tmp_path,
        match_results=[_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])],
    )
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    monkeypatch.setattr(
        "amm_competition.hill_climb.harness.ProtectedSurfaceChecker.discover",
        lambda: _NoopProtectedSurfaceChecker(),
    )

    mixed_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        stage="screen",
        baseline_eval_id="screen_0001",
        candidate_eval_id=None,
        anchor_eval_id=None,
        baseline_source=str(source_path),
        candidate_source=str(source_path),
        anchor_source=None,
        read_only=False,
        json=False,
    )
    assert hill_climb_compare_profiles_command(mixed_args) == 1
    assert (
        "Choose either --baseline-eval-id or --baseline-source, not both"
        in capsys.readouterr().out
    )

    stage_args = argparse.Namespace(
        run_id="mar26",
        artifact_root=str(tmp_path / "artifacts"),
        stage="climb",
        baseline_eval_id="screen_0001",
        candidate_eval_id="screen_0001",
        anchor_eval_id=None,
        baseline_source=None,
        candidate_source=None,
        anchor_source=None,
        read_only=False,
        json=False,
    )
    assert hill_climb_compare_profiles_command(stage_args) == 1
    assert (
        "is for stage 'screen', not requested stage 'climb'" in capsys.readouterr().out
    )
