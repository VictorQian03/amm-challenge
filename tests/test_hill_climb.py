"""Tests for the thin hill-climb harness."""

import argparse
from decimal import Decimal
import json
from pathlib import Path
import subprocess
from typing import Any, cast

import pytest

from amm_competition.cli import (
    hill_climb_compare_profiles_command,
    hill_climb_probe_command,
    hill_climb_status_command,
)
from amm_competition.competition.match import LightweightSimResult, MatchResult
from amm_competition.competition.protected_surface import (
    ProtectedSurfaceChecker,
    ProtectedSurfaceFingerprint,
    ProtectedSurfaceError,
)
from amm_competition.hill_climb.harness import HillClimbHarness, HillClimbHarnessError
from amm_competition.hill_climb.stages import (
    HILL_CLIMB_STAGES,
    build_stage_config,
    build_stage_runner,
)
from amm_competition.competition.config import BASELINE_SETTINGS


def _metric_value(value: float | list[float], index: int) -> float:
    if isinstance(value, list):
        return value[index]
    return value


def _make_match_result(
    *,
    mean_edges: list[float],
    retail_edges: float | list[float] = 5.0,
    arb_edges: float | list[float] = -1.0,
    max_fee_jumps: float | list[float] = 0.001,
    time_weighted_bid_fees: float | list[float] = 0.0075,
    time_weighted_ask_fees: float | list[float] = 0.0075,
    gbm_sigmas: float | list[float] = 0.00095,
    retail_arrival_rates: float | list[float] = 0.8,
    retail_mean_sizes: float | list[float] = 20.0,
    retail_volumes: float | list[float] = 10.0,
    arb_volumes: float | list[float] = 2.0,
) -> MatchResult:
    simulation_results = []
    for seed, candidate_edge in enumerate(mean_edges):
        benchmark_edge = candidate_edge - 1.0
        retail_edge = _metric_value(retail_edges, seed)
        arb_edge = _metric_value(arb_edges, seed)
        max_fee_jump = _metric_value(max_fee_jumps, seed)
        bid_fee = _metric_value(time_weighted_bid_fees, seed)
        ask_fee = _metric_value(time_weighted_ask_fees, seed)
        gbm_sigma = _metric_value(gbm_sigmas, seed)
        retail_arrival_rate = _metric_value(retail_arrival_rates, seed)
        retail_mean_size = _metric_value(retail_mean_sizes, seed)
        retail_volume = _metric_value(retail_volumes, seed)
        arb_volume = _metric_value(arb_volumes, seed)
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
                arb_volume_y={"submission": arb_volume, "normalizer": 1.0},
                retail_volume_y={"submission": retail_volume, "normalizer": 5.0},
                average_fees={
                    "submission": (bid_fee, ask_fee),
                    "normalizer": (0.003, 0.003),
                },
                gbm_sigma=gbm_sigma,
                retail_arrival_rate=retail_arrival_rate,
                retail_mean_size=retail_mean_size,
                retail_edge={"submission": retail_edge, "normalizer": 4.0},
                arb_edge={"submission": arb_edge, "normalizer": -1.0},
                retail_trade_count={"submission": 3, "normalizer": 2},
                arb_trade_count={"submission": 1, "normalizer": 1},
                max_fee_jump={"submission": max_fee_jump, "normalizer": 0.0},
                time_weighted_fees={
                    "submission": (bid_fee, ask_fee),
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


def _git(args: list[str], *, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def _build_protected_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    protected_path = repo_root / "amm_competition" / "competition" / "config.py"
    strategy_path = repo_root / "contracts" / "src" / "StarterStrategy.sol"
    protected_path.parent.mkdir(parents=True)
    strategy_path.parent.mkdir(parents=True)
    (repo_root / ".competition-protected-paths").write_text(
        "amm_competition/competition/config.py\n"
    )
    protected_path.write_text("BASELINE = 1\n")
    strategy_path.write_text("// starter\n")

    _git(["git", "init"], cwd=repo_root)
    _git(["git", "config", "user.name", "Test User"], cwd=repo_root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=repo_root)
    _git(["git", "add", "."], cwd=repo_root)
    _git(["git", "commit", "-m", "init"], cwd=repo_root)
    return repo_root, strategy_path


class _StubStrategy:
    def __init__(self, name: str = "Candidate") -> None:
        self._name = name

    @property
    def bytecode(self) -> bytes:
        return b"\x60\x00"

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
    artifact_root: Path | None = None,
    protected_surface_checker: Any | None = None,
) -> HillClimbHarness:
    return HillClimbHarness(
        artifact_root=artifact_root or (tmp_path / "artifacts" / "hill_climb"),
        n_workers=1,
        strategy_loader=cast(Any, strategy_loader or _FixedStrategyLoader()),
        baseline_loader=lambda: object(),
        stage_runner_factory=_SequentialRunnerFactory(
            match_results or [_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])]
        ),
        protected_surface_checker=protected_surface_checker or _NoopProtectedSurfaceChecker(),
    )


def test_hill_climb_stages_keep_competition_length_steps():
    assert build_stage_config().n_steps == BASELINE_SETTINGS.n_steps


def test_build_stage_runner_uses_hill_climb_stage_seed_block():
    runner = build_stage_runner("screen", n_workers=1)
    assert runner.seed_block == HILL_CLIMB_STAGES["screen"].seed_block


def test_evaluate_records_seed_keep_and_discard(tmp_path):
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
            _make_match_result(mean_edges=[5.2, 5.2, 5.2, 5.2]),
        ],
    )
    source_path = tmp_path / "StarterStrategy.sol"

    source_path.write_text("// variant 1\n")
    first = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    source_path.write_text("// variant 2\n")
    second = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    source_path.write_text("// variant 3\n")
    third = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    assert first["status"] == "seed"
    assert second["status"] == "keep"
    assert third["status"] == "discard"

    run_dir = tmp_path / "artifacts" / "hill_climb" / "mar26"
    results = [json.loads(line) for line in (run_dir / "results.jsonl").read_text().splitlines()]
    assert [entry["status"] for entry in results] == ["seed", "keep", "discard"]
    manifest = json.loads((run_dir / "run.json").read_text())
    assert manifest["artifact_version"] == "hill_climb.run.v2"
    assert manifest["eval_count"] == 3
    assert manifest["snapshot_count"] == 3
    assert not (run_dir / "results.tsv").exists()
    assert not (run_dir / "history.jsonl").exists()
    assert not (run_dir / "incumbents").exists()
    status = harness.get_run_status(run_id="mar26")
    assert status["stages"]["screen"]["incumbent"]["eval_id"] == second["eval_id"]
    index_payload = json.loads(
        (tmp_path / "artifacts" / "hill_climb" / "index.json").read_text()
    )
    assert index_payload["runs"][0]["run_id"] == "mar26"
    assert index_payload["runs"][0]["status"] == "active"


def test_evaluate_records_invalid_eval_on_failure(tmp_path):
    harness = _build_test_harness(
        tmp_path,
        strategy_loader=_SequentialStrategyLoader([RuntimeError("bad compile")]),
    )
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// invalid\n")

    with pytest.raises(HillClimbHarnessError, match="bad compile"):
        harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    run_dir = tmp_path / "artifacts" / "hill_climb" / "mar26"
    results = [json.loads(line) for line in (run_dir / "results.jsonl").read_text().splitlines()]
    assert results[0]["status"] == "invalid"
    assert results[0]["derived_analysis"]["failure_signature"]["primary_tag"] == "invalid_eval"


def test_evaluate_rejects_same_stage_duplicate_source_without_replay_reason(tmp_path):
    harness = _build_test_harness(tmp_path)
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// stable\n")

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    with pytest.raises(HillClimbHarnessError, match="already evaluated source"):
        harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)


def test_evaluate_allows_same_stage_duplicate_source_with_replay_reason(tmp_path):
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
        ],
    )
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// stable\n")

    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    replay = harness.evaluate(
        run_id="mar26",
        stage="screen",
        source_path=source_path,
        replay_reason="confirm deterministic behavior",
    )
    assert replay["replay_reason"] == "confirm deterministic behavior"


def test_evaluate_rejects_worker_style_run_id_in_retained_root(tmp_path):
    harness = _build_test_harness(tmp_path)
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// worker\n")

    with pytest.raises(HillClimbHarnessError, match="scratch-only"):
        harness.evaluate(
            run_id="apr21-screen490-1431-w1-tailfloor",
            stage="screen",
            source_path=source_path,
        )


def test_probe_source_returns_gate_without_persisting_run_artifacts(tmp_path):
    harness = _build_test_harness(tmp_path)
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// probe\n")

    payload = harness.probe_source(stage="screen", source_path=source_path)

    assert payload["mode"] == "probe"
    assert payload["stage"] == "screen"
    assert payload["selection"]["rationale"] == "probe only; not recorded in the retained lane"
    assert not (tmp_path / "artifacts" / "hill_climb").exists()


def test_status_history_show_eval_and_pull_best(tmp_path):
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
        ],
    )
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// variant 1\n")
    first = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    source_path.write_text("// variant 2\n")
    second = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    status = harness.get_run_status(run_id="mar26")
    assert status["stages"]["screen"]["incumbent"]["eval_id"] == second["eval_id"]
    assert status["stages"]["screen"]["best_raw"]["eval_id"] == second["eval_id"]
    assert status["latest"]["eval_id"] == second["eval_id"]

    history = harness.get_history(run_id="mar26")
    assert [entry["eval_id"] for entry in history] == [first["eval_id"], second["eval_id"]]

    fetched = harness.get_evaluation(run_id="mar26", eval_id=second["eval_id"])
    assert fetched["eval_id"] == second["eval_id"]

    destination = tmp_path / "restored.sol"
    harness.pull_best(run_id="mar26", stage="screen", destination=destination)
    assert destination.read_text() == source_path.read_text()


def test_cross_run_index_marks_newest_valid_run_active(tmp_path):
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
        ],
    )
    source_path = tmp_path / "StarterStrategy.sol"

    source_path.write_text("// run a\n")
    harness.evaluate(run_id="older", stage="screen", source_path=source_path)
    source_path.write_text("// run b\n")
    harness.evaluate(run_id="newer", stage="screen", source_path=source_path)

    payload = harness.list_runs()
    statuses = {entry["run_id"]: entry["status"] for entry in payload["runs"]}
    assert statuses["newer"] == "active"
    assert statuses["older"] == "historical"


def test_status_rejects_manifest_layout_drift(tmp_path):
    harness = _build_test_harness(tmp_path)
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// variant 1\n")
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    run_dir = tmp_path / "artifacts" / "hill_climb" / "mar26"
    manifest_path = run_dir / "run.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["eval_count"] = 99
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    with pytest.raises(
        HillClimbHarnessError,
        match="manifest eval_count does not match results.jsonl",
    ):
        harness.get_run_status(run_id="mar26")


def test_status_rejects_legacy_retained_surfaces(tmp_path):
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[6.0, 6.0, 6.0, 6.0]),
        ],
    )
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// variant 1\n")
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)
    source_path.write_text("// variant 2\n")
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    run_dir = tmp_path / "artifacts" / "hill_climb" / "mar26"
    (run_dir / "results.tsv").write_text("legacy\n")

    with pytest.raises(
        HillClimbHarnessError,
        match="unexpected legacy retained artifacts",
    ):
        harness.get_run_status(run_id="mar26")


def test_read_commands_allow_protected_surface_drift(tmp_path):
    repo_root, strategy_path = _build_protected_repo(tmp_path)
    artifact_root = repo_root / "artifacts" / "hill_climb"
    checker = ProtectedSurfaceChecker(repo_root=repo_root)
    harness = _build_test_harness(
        tmp_path,
        artifact_root=artifact_root,
        protected_surface_checker=checker,
    )

    harness.evaluate(run_id="mar26", stage="screen", source_path=strategy_path)
    (repo_root / "amm_competition" / "competition" / "config.py").write_text("BASELINE = 2\n")

    with pytest.raises(HillClimbHarnessError, match="different protected competition mechanics surface"):
        harness.get_run_status(run_id="mar26")

    status = harness.get_run_status(
        run_id="mar26",
        allow_protected_surface_drift=True,
    )
    assert status["warnings"]
    assert "different protected competition mechanics surface" in status["warnings"][0]


def test_compare_profiles_source_blocks_dirty_protected_surface(tmp_path):
    repo_root, strategy_path = _build_protected_repo(tmp_path)
    artifact_root = repo_root / "artifacts" / "hill_climb"
    checker = ProtectedSurfaceChecker(repo_root=repo_root)
    harness = _build_test_harness(
        tmp_path,
        artifact_root=artifact_root,
        protected_surface_checker=checker,
    )

    stored = harness.evaluate(run_id="mar26", stage="screen", source_path=strategy_path)
    (repo_root / "amm_competition" / "competition" / "config.py").write_text("BASELINE = 2\n")

    with pytest.raises(ProtectedSurfaceError, match="protected competition mechanics"):
        harness.compare_profiles(
            stage="screen",
            baseline_summary=stored,
            candidate_source_path=strategy_path,
        )


def test_compare_profiles_supports_stored_eval_and_source(tmp_path):
    harness = _build_test_harness(
        tmp_path,
        match_results=[
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
            _make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0]),
        ],
    )
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// baseline\n")
    stored = harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    payload = harness.compare_profiles(
        stage="screen",
        baseline_summary=stored,
        candidate_source_path=source_path,
    )
    assert payload["baseline"]["kind"] == "stored_eval"
    assert payload["candidate"]["kind"] == "source"
    assert "mean_edge" in payload["candidate_vs_baseline"]


def test_status_command_renders_text_for_thin_surface(tmp_path, capsys, monkeypatch):
    harness = _build_test_harness(
        tmp_path,
        match_results=[_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])],
    )
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// variant\n")
    harness.evaluate(run_id="mar26", stage="screen", source_path=source_path)

    args = argparse.Namespace(
        run_id="mar26",
        stage=None,
        artifact_root=str(tmp_path / "artifacts" / "hill_climb"),
        read_only=False,
        json=False,
    )
    monkeypatch.setattr("amm_competition.cli.HillClimbHarness", lambda artifact_root: harness)
    assert hill_climb_status_command(args) == 0
    output = capsys.readouterr().out
    assert "Run ID: mar26" in output
    assert "Evals: 1" in output
    assert "screen:" in output
    assert "Incumbent:" in output


def test_probe_command_renders_without_persisting_artifacts(tmp_path, capsys, monkeypatch):
    harness = _build_test_harness(
        tmp_path,
        match_results=[_make_match_result(mean_edges=[5.0, 5.0, 5.0, 5.0])],
    )
    source_path = tmp_path / "StarterStrategy.sol"
    source_path.write_text("// probe\n")

    args = argparse.Namespace(
        stage="screen",
        strategy=str(source_path),
        json=False,
    )
    monkeypatch.setattr("amm_competition.cli.HillClimbHarness", lambda: harness)
    assert hill_climb_probe_command(args) == 0
    output = capsys.readouterr().out
    assert "Mode: probe" in output
    assert "Selection: probe only; not recorded in the retained lane" in output
    assert not (tmp_path / "artifacts" / "hill_climb").exists()


def test_compare_profiles_command_requires_run_id_for_eval_ids(capsys):
    args = argparse.Namespace(
        stage="screen",
        run_id=None,
        artifact_root="artifacts/hill_climb",
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
    output = capsys.readouterr().out
    assert "--run-id is required" in output


def test_stable_hill_climb_docs_do_not_reference_removed_queue_surfaces():
    stale_patterns = (
        "hill-climb analyze-run",
        "hill-climb set-hypothesis",
        "hill-climb set-state",
        "hill-climb show-hypothesis",
    )

    for relpath in ("docs/hill_climb.md", "README.md"):
        text = Path(relpath).read_text()
        for pattern in stale_patterns:
            assert pattern not in text

    readme_text = Path("README.md").read_text()
    assert "queued-hypothesis" not in readme_text
    assert "hypothesis registry" not in readme_text

    docs_text = Path("docs/hill_climb.md").read_text()
    assert "docs/plans/active/" in docs_text
    assert "artifacts/scratch_probes/<run_id>/" in docs_text
