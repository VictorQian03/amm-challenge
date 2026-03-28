"""Tests for deterministic scorecard computation."""

from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest

from amm_competition.competition.eval import compute_scorecard
from amm_competition.competition.match import LightweightSimResult, MatchResult


def _make_sim_result(
    *,
    seed: int,
    submission_edge: str,
    normalizer_edge: str,
    gbm_sigma: float,
    retail_arrival_rate: float,
    retail_mean_size: float,
    submission_retail_volume: float,
    normalizer_retail_volume: float,
    submission_arb_volume: float,
    submission_retail_edge: float = 4.0,
    submission_arb_edge: float = -1.0,
    submission_retail_trade_count: int = 3,
    submission_arb_trade_count: int = 1,
    submission_max_fee_jump: float = 0.001,
    submission_time_weighted_bid_fee: float = 0.003,
    submission_time_weighted_ask_fee: float = 0.004,
) -> LightweightSimResult:
    return LightweightSimResult(
        seed=seed,
        strategies=["submission", "normalizer"],
        pnl={
            "submission": Decimal(submission_edge),
            "normalizer": Decimal(normalizer_edge),
        },
        edges={
            "submission": Decimal(submission_edge),
            "normalizer": Decimal(normalizer_edge),
        },
        initial_fair_price=100.0,
        initial_reserves={
            "submission": (100.0, 10000.0),
            "normalizer": (100.0, 10000.0),
        },
        steps=[],
        arb_volume_y={"submission": submission_arb_volume, "normalizer": 1.0},
        retail_volume_y={
            "submission": submission_retail_volume,
            "normalizer": normalizer_retail_volume,
        },
        average_fees={"submission": (0.003, 0.004), "normalizer": (0.003, 0.003)},
        gbm_sigma=gbm_sigma,
        retail_arrival_rate=retail_arrival_rate,
        retail_mean_size=retail_mean_size,
        retail_edge={"submission": submission_retail_edge, "normalizer": 1.0},
        arb_edge={"submission": submission_arb_edge, "normalizer": -0.5},
        retail_trade_count={
            "submission": submission_retail_trade_count,
            "normalizer": 2,
        },
        arb_trade_count={
            "submission": submission_arb_trade_count,
            "normalizer": 1,
        },
        max_fee_jump={"submission": submission_max_fee_jump, "normalizer": 0.0},
        time_weighted_fees={
            "submission": (
                submission_time_weighted_bid_fee,
                submission_time_weighted_ask_fee,
            ),
            "normalizer": (0.003, 0.003),
        },
    )


def _make_match_result(sim_results: list[Any]) -> MatchResult:
    wins_a = sum(
        result.edges["submission"] > result.edges["normalizer"]
        for result in sim_results
    )
    wins_b = sum(
        result.edges["normalizer"] > result.edges["submission"]
        for result in sim_results
    )
    draws = len(sim_results) - wins_a - wins_b
    return MatchResult(
        strategy_a="candidate",
        strategy_b="benchmark",
        wins_a=wins_a,
        wins_b=wins_b,
        draws=draws,
        total_pnl_a=sum(
            (result.pnl["submission"] for result in sim_results), Decimal("0")
        ),
        total_pnl_b=sum(
            (result.pnl["normalizer"] for result in sim_results), Decimal("0")
        ),
        total_edge_a=sum(
            (result.edges["submission"] for result in sim_results), Decimal("0")
        ),
        total_edge_b=sum(
            (result.edges["normalizer"] for result in sim_results), Decimal("0")
        ),
        simulation_results=sim_results,
    )


def test_compute_scorecard_is_deterministic_and_json_ready():
    sim_results = [
        _make_sim_result(
            seed=seed,
            submission_edge=str(seed + 1),
            normalizer_edge=str(seed),
            gbm_sigma=0.1 + (seed * 0.1),
            retail_arrival_rate=1.0 + seed,
            retail_mean_size=2.0,
            submission_retail_volume=10.0,
            normalizer_retail_volume=5.0,
            submission_arb_volume=2.0,
            submission_max_fee_jump=0.001 * (seed + 1),
        )
        for seed in range(6)
    ]
    match_result = _make_match_result(sim_results)

    first = compute_scorecard(match_result, stage="fast_screen")
    second = compute_scorecard(match_result, stage="fast_screen")

    assert first == second
    assert first["scorecard_version"] == "1.2"
    assert first["run_metadata"]["telemetry_version"] == "1.1"
    assert first["overall"]["mean_edge"] == pytest.approx(3.5)
    assert first["overall"]["benchmark_mean_edge"] == pytest.approx(2.5)
    assert first["overall"]["mean_edge_delta"] == pytest.approx(1.0)
    assert first["overall"]["retail_volume_share"] == pytest.approx(2 / 3)
    assert first["overall"]["arb_to_retail_volume_ratio"] == pytest.approx(0.2)
    assert first["overall"]["retail_edge"] == pytest.approx(4.0)
    assert first["overall"]["arb_edge"] == pytest.approx(-1.0)
    assert first["overall"]["retail_flow_share"] == pytest.approx(10 / 12)
    assert first["overall"]["arb_flow_share"] == pytest.approx(2 / 12)
    assert first["overall"]["retail_gain_share"] == pytest.approx(0.8)
    assert first["overall"]["arb_loss_share"] == pytest.approx(0.2)
    assert first["overall"]["retail_trade_count"] == pytest.approx(3.0)
    assert first["overall"]["arb_trade_count"] == pytest.approx(1.0)
    assert first["overall"]["max_fee_jump"] == pytest.approx(0.0035)
    assert first["overall"]["time_weighted_bid_fee"] == pytest.approx(0.003)
    assert first["overall"]["time_weighted_ask_fee"] == pytest.approx(0.004)
    assert first["overall"]["arb_loss_to_retail_gain"] == pytest.approx(0.25)
    assert first["overall"]["min_edge"] == pytest.approx(1.0)
    assert first["overall"]["max_edge"] == pytest.approx(6.0)
    assert first["overall"]["edge_stddev"] == pytest.approx(1.707825127659933)
    assert first["gate"]["passed"] is True
    assert first["gate"]["thresholds"] == {"mean_edge": 0.0}

    volatility = first["by_slice"]["volatility_terciles"]
    assert volatility["low"]["simulation_count"] == 2
    assert volatility["mid"]["simulation_count"] == 2
    assert volatility["high"]["simulation_count"] == 2
    assert (
        sum(
            bucket["simulation_count"]
            for bucket in first["by_slice"]["mean_edge_deciles"].values()
        )
        == 6
    )
    empty_deciles = [
        bucket
        for bucket in first["by_slice"]["mean_edge_deciles"].values()
        if bucket["simulation_count"] == 0
    ]
    assert empty_deciles
    for bucket in empty_deciles:
        assert bucket["benchmark_mean_edge"] is None
        assert bucket["mean_edge_delta"] is None


def test_compute_scorecard_rejects_missing_required_diagnostics():
    sim_result = _make_sim_result(
        seed=1,
        submission_edge="2.0",
        normalizer_edge="1.0",
        gbm_sigma=0.2,
        retail_arrival_rate=1.0,
        retail_mean_size=2.0,
        submission_retail_volume=4.0,
        normalizer_retail_volume=3.0,
        submission_arb_volume=1.0,
    )
    sim_result.time_weighted_fees = {}

    with pytest.raises(ValueError, match="time_weighted_fees"):
        compute_scorecard(_make_match_result([sim_result]), stage="fast_screen")


def test_compute_scorecard_requires_stored_results():
    match_result = MatchResult(
        strategy_a="candidate",
        strategy_b="benchmark",
        wins_a=0,
        wins_b=0,
        draws=0,
        total_pnl_a=Decimal("0"),
        total_pnl_b=Decimal("0"),
        total_edge_a=Decimal("0"),
        total_edge_b=Decimal("0"),
        simulation_results=[],
    )

    with pytest.raises(ValueError, match="store_results=True"):
        compute_scorecard(match_result)


def test_compute_scorecard_rejects_duplicate_seed_results():
    duplicate_seed = [
        _make_sim_result(
            seed=7,
            submission_edge="2.0",
            normalizer_edge="1.0",
            gbm_sigma=0.2,
            retail_arrival_rate=1.0,
            retail_mean_size=2.0,
            submission_retail_volume=4.0,
            normalizer_retail_volume=3.0,
            submission_arb_volume=1.0,
        ),
        _make_sim_result(
            seed=7,
            submission_edge="1.5",
            normalizer_edge="1.0",
            gbm_sigma=0.3,
            retail_arrival_rate=1.5,
            retail_mean_size=2.0,
            submission_retail_volume=4.0,
            normalizer_retail_volume=3.0,
            submission_arb_volume=1.0,
        ),
    ]

    with pytest.raises(ValueError, match="Duplicate stored simulation seed"):
        compute_scorecard(_make_match_result(duplicate_seed))


def test_compute_scorecard_rejects_missing_required_fields():
    broken_result = SimpleNamespace(
        **_make_sim_result(
            seed=1,
            submission_edge="2.0",
            normalizer_edge="1.0",
            gbm_sigma=0.2,
            retail_arrival_rate=1.0,
            retail_mean_size=2.0,
            submission_retail_volume=4.0,
            normalizer_retail_volume=3.0,
            submission_arb_volume=1.0,
        ).__dict__
    )
    del broken_result.gbm_sigma

    with pytest.raises(ValueError, match="gbm_sigma"):
        compute_scorecard(_make_match_result([broken_result]))


def test_compute_scorecard_enforces_same_seed_delta_threshold() -> None:
    sim_results = [
        _make_sim_result(
            seed=seed,
            submission_edge=str(seed),
            normalizer_edge=str(seed),
            gbm_sigma=0.1,
            retail_arrival_rate=1.0,
            retail_mean_size=2.0,
            submission_retail_volume=10.0,
            normalizer_retail_volume=5.0,
            submission_arb_volume=2.0,
        )
        for seed in range(4)
    ]

    scorecard = compute_scorecard(
        _make_match_result(sim_results), stage="final_confidence"
    )

    assert scorecard["overall"]["mean_edge_delta"] == pytest.approx(0.0)
    assert scorecard["gate"]["thresholds"] == {
        "mean_edge": 0.0,
        "mean_edge_delta": 0.0,
    }
    assert scorecard["gate"]["passed"] is True

    worse = compute_scorecard(
        _make_match_result(
            [
                _make_sim_result(
                    seed=seed,
                    submission_edge=str(seed),
                    normalizer_edge=str(seed + 0.5),
                    gbm_sigma=0.1,
                    retail_arrival_rate=1.0,
                    retail_mean_size=2.0,
                    submission_retail_volume=10.0,
                    normalizer_retail_volume=5.0,
                    submission_arb_volume=2.0,
                )
                for seed in range(4)
            ]
        ),
        stage="final_confidence",
    )

    assert worse["overall"]["mean_edge_delta"] == pytest.approx(-0.5)
    assert worse["gate"]["passed"] is False
    assert "mean_edge_delta" in worse["gate"]["failures"][0]
