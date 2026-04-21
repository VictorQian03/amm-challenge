"""Tests for deterministic scorecard computation."""

from dataclasses import replace
from decimal import Decimal

import pytest

from amm_competition.competition.eval import compute_scorecard
from amm_competition.competition.match import LightweightSimResult, MatchResult


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


def test_compute_scorecard_requires_store_results():
    result = MatchResult(
        strategy_a="candidate",
        strategy_b="normalizer",
        wins_a=1,
        wins_b=0,
        draws=0,
        total_pnl_a=Decimal("1"),
        total_pnl_b=Decimal("0"),
        total_edge_a=Decimal("1"),
        total_edge_b=Decimal("0"),
        simulation_results=[],
    )
    with pytest.raises(ValueError, match="store_results=True"):
        compute_scorecard(result)


def test_compute_scorecard_surfaces_overall_and_slice_metrics():
    scorecard = compute_scorecard(
        _make_match_result(
            mean_edges=[5.0, 6.0, 7.0, 8.0],
            retail_edges=[6.0, 6.5, 7.0, 7.5],
            arb_edges=[-1.0, -1.1, -1.2, -1.3],
            retail_arrival_rates=[0.6, 0.7, 0.8, 0.9],
            retail_mean_sizes=[18.0, 19.0, 20.0, 21.0],
            gbm_sigmas=[0.0008, 0.0009, 0.0010, 0.0011],
        )
    )

    overall = scorecard["overall"]
    assert overall["simulation_count"] == 4
    assert overall["mean_edge"] == pytest.approx(6.5)
    assert overall["benchmark_mean_edge"] == pytest.approx(5.5)
    assert overall["mean_edge_delta"] == pytest.approx(1.0)
    assert overall["retail_volume_share"] is not None
    assert overall["arb_to_retail_volume_ratio"] is not None
    assert overall["quote_selectivity_ratio"] is not None
    assert scorecard["by_slice"]["volatility_terciles"]["low"]["simulation_count"] >= 1
    assert scorecard["metric_fields"]["required_gate_metrics"] == [
        "mean_edge",
        "retail_volume_share",
        "arb_to_retail_volume_ratio",
    ]


def test_compute_scorecard_rejects_duplicate_seeds():
    result = _make_match_result(mean_edges=[5.0, 6.0])
    result.simulation_results[1] = replace(
        result.simulation_results[1],
        seed=result.simulation_results[0].seed,
    )
    with pytest.raises(ValueError, match="Duplicate stored simulation seed"):
        compute_scorecard(result)
