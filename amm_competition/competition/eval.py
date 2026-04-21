"""Deterministic scorecard computation for stored benchmark match results."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from typing import Any

from amm_competition.competition.match import LightweightSimResult, MatchResult

SUBMISSION_KEY = "submission"
NORMALIZER_KEY = "normalizer"
EPSILON = 1e-9
SCORECARD_VERSION = "thin-scorecard.v1"
TELEMETRY_VERSION = "1.2"

REQUIRED_GATE_METRIC_FIELDS = (
    "mean_edge",
    "retail_volume_share",
    "arb_to_retail_volume_ratio",
)

OPTIONAL_DIAGNOSTIC_METRIC_FIELDS = (
    "benchmark_mean_edge",
    "mean_edge_delta",
    "retail_edge",
    "arb_edge",
    "retail_flow_share",
    "arb_flow_share",
    "retail_gain_share",
    "arb_loss_share",
    "retail_trade_count",
    "arb_trade_count",
    "max_fee_jump",
    "time_weighted_bid_fee",
    "time_weighted_ask_fee",
    "time_weighted_mean_fee",
    "arb_loss_to_retail_gain",
    "quote_selectivity_ratio",
    "min_edge",
    "max_edge",
    "edge_stddev",
)

SCORECARD_METRIC_FIELDS = (
    REQUIRED_GATE_METRIC_FIELDS + OPTIONAL_DIAGNOSTIC_METRIC_FIELDS
)
REQUIRED_SIMULATION_RESULT_FIELDS = (
    "gbm_sigma",
    "retail_arrival_rate",
    "retail_mean_size",
)
REQUIRED_SIMULATION_RESULT_MAP_FIELDS = {
    "edges": ("submission", "normalizer"),
    "retail_volume_y": ("submission", "normalizer"),
    "arb_volume_y": ("submission",),
    "retail_edge": ("submission", "normalizer"),
    "arb_edge": ("submission", "normalizer"),
    "retail_trade_count": ("submission", "normalizer"),
    "arb_trade_count": ("submission", "normalizer"),
    "max_fee_jump": ("submission", "normalizer"),
    "time_weighted_fees": ("submission", "normalizer"),
    "average_fees": ("submission", "normalizer"),
}


@dataclass(frozen=True)
class ScorecardRecord:
    seed: int
    mean_edge: float
    benchmark_mean_edge: float
    mean_edge_delta: float
    gbm_sigma: float
    retail_arrival_rate: float
    retail_mean_size: float
    retail_intensity: float
    submission_retail_volume: float
    normalizer_retail_volume: float
    submission_arb_volume: float
    retail_edge: float
    arb_edge: float
    retail_trade_count: int
    arb_trade_count: int
    max_fee_jump: float
    time_weighted_bid_fee: float
    time_weighted_ask_fee: float


def compute_scorecard(match_result: MatchResult) -> dict[str, Any]:
    """Compute a deterministic scorecard from stored per-seed match results."""
    records = _extract_records(match_result)
    return {
        "scorecard_version": SCORECARD_VERSION,
        "run_metadata": {
            "simulation_count": len(records),
            "seeds": [record.seed for record in records],
            "telemetry_version": TELEMETRY_VERSION,
        },
        "seed_records": [
            {
                "seed": record.seed,
                "mean_edge": record.mean_edge,
                "benchmark_mean_edge": record.benchmark_mean_edge,
                "mean_edge_delta": record.mean_edge_delta,
                "gbm_sigma": record.gbm_sigma,
                "retail_arrival_rate": record.retail_arrival_rate,
                "retail_mean_size": record.retail_mean_size,
                "retail_intensity": record.retail_intensity,
            }
            for record in records
        ],
        "overall": _summarize_records(records),
        "by_slice": {
            "volatility_terciles": _bucket_summary(
                records,
                value_key="gbm_sigma",
                labels=("low", "mid", "high"),
            ),
            "arrival_rate_terciles": _bucket_summary(
                records,
                value_key="retail_arrival_rate",
                labels=("low", "mid", "high"),
            ),
            "retail_mean_size_terciles": _bucket_summary(
                records,
                value_key="retail_mean_size",
                labels=("low", "mid", "high"),
            ),
            "retail_intensity_terciles": _bucket_summary(
                records,
                value_key="retail_intensity",
                labels=("low", "mid", "high"),
            ),
            "arrival_rate_x_volatility_terciles": _grid_bucket_summary(
                records,
                row_value_key="retail_arrival_rate",
                row_labels=("low", "mid", "high"),
                column_value_key="gbm_sigma",
                column_labels=("low", "mid", "high"),
            ),
            "mean_edge_deciles": _bucket_summary(
                records,
                value_key="mean_edge",
                labels=tuple(f"d{i:02d}" for i in range(1, 11)),
            ),
        },
        "metric_fields": {
            "required_gate_metrics": list(REQUIRED_GATE_METRIC_FIELDS),
            "diagnostic_metrics": list(OPTIONAL_DIAGNOSTIC_METRIC_FIELDS),
        },
    }


def _extract_records(match_result: MatchResult) -> list[ScorecardRecord]:
    simulation_results = match_result.simulation_results
    if not simulation_results:
        raise ValueError(
            "Scorecard requires store_results=True and seed-level simulation_results"
        )
    if len(simulation_results) != match_result.total_games:
        raise ValueError(
            "Stored simulation_results count must match total_games; "
            f"got {len(simulation_results)} results for {match_result.total_games} games"
        )

    records: list[ScorecardRecord] = []
    seen_seeds: set[int] = set()
    for result in simulation_results:
        _validate_simulation_result(result)
        seed = int(result.seed)
        if seed in seen_seeds:
            raise ValueError(f"Duplicate stored simulation seed encountered: {seed}")
        seen_seeds.add(seed)

        submission_edge = _required_float(result.edges, SUBMISSION_KEY, field_name="edges")
        benchmark_edge = _required_float(result.edges, NORMALIZER_KEY, field_name="edges")
        submission_retail_volume = _required_float(
            result.retail_volume_y,
            SUBMISSION_KEY,
            field_name="retail_volume_y",
        )
        normalizer_retail_volume = _required_float(
            result.retail_volume_y,
            NORMALIZER_KEY,
            field_name="retail_volume_y",
        )
        submission_arb_volume = _required_float(
            result.arb_volume_y,
            SUBMISSION_KEY,
            field_name="arb_volume_y",
        )

        records.append(
            ScorecardRecord(
                seed=seed,
                mean_edge=submission_edge,
                benchmark_mean_edge=benchmark_edge,
                mean_edge_delta=submission_edge - benchmark_edge,
                gbm_sigma=float(result.gbm_sigma),
                retail_arrival_rate=float(result.retail_arrival_rate),
                retail_mean_size=float(result.retail_mean_size),
                retail_intensity=float(result.retail_arrival_rate * result.retail_mean_size),
                submission_retail_volume=submission_retail_volume,
                normalizer_retail_volume=normalizer_retail_volume,
                submission_arb_volume=submission_arb_volume,
                retail_edge=_required_float(
                    result.retail_edge,
                    SUBMISSION_KEY,
                    field_name="retail_edge",
                ),
                arb_edge=_required_float(
                    result.arb_edge,
                    SUBMISSION_KEY,
                    field_name="arb_edge",
                ),
                retail_trade_count=_required_int(
                    result.retail_trade_count,
                    SUBMISSION_KEY,
                    field_name="retail_trade_count",
                ),
                arb_trade_count=_required_int(
                    result.arb_trade_count,
                    SUBMISSION_KEY,
                    field_name="arb_trade_count",
                ),
                max_fee_jump=_required_float(
                    result.max_fee_jump,
                    SUBMISSION_KEY,
                    field_name="max_fee_jump",
                ),
                time_weighted_bid_fee=_required_tuple_float(
                    result.time_weighted_fees,
                    SUBMISSION_KEY,
                    field_name="time_weighted_fees",
                    index=0,
                ),
                time_weighted_ask_fee=_required_tuple_float(
                    result.time_weighted_fees,
                    SUBMISSION_KEY,
                    field_name="time_weighted_fees",
                    index=1,
                ),
            )
        )

    return sorted(records, key=lambda record: record.seed)


def _validate_simulation_result(result: LightweightSimResult) -> None:
    for attribute in REQUIRED_SIMULATION_RESULT_FIELDS:
        if getattr(result, attribute, None) is None:
            raise ValueError(
                f"Stored simulation result missing required field: {attribute}"
            )

    for field_name, required_keys in REQUIRED_SIMULATION_RESULT_MAP_FIELDS.items():
        mapping = _require_simulation_result_mapping(result, field_name)
        for key in required_keys:
            if key not in mapping:
                raise ValueError(
                    f"Stored simulation result missing required key '{key}' in {field_name}"
                )


def _required_map_value(
    mapping: Mapping[str, Any],
    key: str,
    *,
    field_name: str,
) -> Any:
    if key not in mapping:
        raise ValueError(
            f"Stored simulation result missing required key '{key}' in {field_name}"
        )
    value = mapping[key]
    if value is None:
        raise ValueError(
            f"Stored simulation result missing required key '{key}' in {field_name}"
        )
    return value


def _required_float(
    mapping: Mapping[str, Any],
    key: str,
    *,
    field_name: str,
) -> float:
    return float(_required_map_value(mapping, key, field_name=field_name))


def _required_int(
    mapping: Mapping[str, Any],
    key: str,
    *,
    field_name: str,
) -> int:
    return int(_required_map_value(mapping, key, field_name=field_name))


def _required_tuple_float(
    mapping: Mapping[str, Any],
    key: str,
    *,
    field_name: str,
    index: int,
) -> float:
    value = _required_map_value(mapping, key, field_name=field_name)
    if not isinstance(value, tuple):
        raise ValueError(
            f"Stored simulation result field {field_name} must contain fee tuples"
        )
    if len(value) <= index:
        raise ValueError(
            f"Stored simulation result field '{field_name}' missing tuple index {index} for key '{key}'"
        )
    return float(value[index])


def _require_simulation_result_mapping(
    result: LightweightSimResult,
    field_name: str,
) -> Mapping[str, Any]:
    try:
        mapping = getattr(result, field_name)
    except AttributeError as exc:
        raise ValueError(
            f"Stored simulation result missing required field: {field_name}"
        ) from exc
    if not isinstance(mapping, Mapping):
        raise ValueError(
            f"Stored simulation result field {field_name} must be a mapping"
        )
    return mapping


def _summarize_records(records: list[ScorecardRecord]) -> dict[str, float | int | None]:
    if not records:
        return {
            "simulation_count": 0,
            **{field: None for field in SCORECARD_METRIC_FIELDS},
        }

    mean_edges = [record.mean_edge for record in records]
    submission_retail = sum(record.submission_retail_volume for record in records)
    normalizer_retail = sum(record.normalizer_retail_volume for record in records)
    submission_arb = sum(record.submission_arb_volume for record in records)

    total_retail = submission_retail + normalizer_retail
    total_submission_flow = submission_retail + submission_arb
    retail_volume_share = None if total_retail <= 0 else submission_retail / total_retail
    arb_to_retail_volume_ratio = (
        None if submission_retail <= 0 else submission_arb / submission_retail
    )
    retail_flow_share = (
        None if total_submission_flow <= 0 else submission_retail / total_submission_flow
    )
    arb_flow_share = None if total_submission_flow <= 0 else submission_arb / total_submission_flow

    retail_edge = _mean([record.retail_edge for record in records])
    arb_edge = _mean([record.arb_edge for record in records])
    retail_gain_share, arb_loss_share = _resolve_edge_shares(
        retail_edge=retail_edge,
        arb_edge=arb_edge,
    )
    retail_trade_count = _mean([float(record.retail_trade_count) for record in records])
    arb_trade_count = _mean([float(record.arb_trade_count) for record in records])
    max_fee_jump = _mean([record.max_fee_jump for record in records])
    time_weighted_bid_fee = _mean([record.time_weighted_bid_fee for record in records])
    time_weighted_ask_fee = _mean([record.time_weighted_ask_fee for record in records])
    time_weighted_mean_fee = None
    if time_weighted_bid_fee is not None and time_weighted_ask_fee is not None:
        time_weighted_mean_fee = (time_weighted_bid_fee + time_weighted_ask_fee) / 2.0

    arb_loss_to_retail_gain = None
    if retail_edge is not None and arb_edge is not None and retail_edge > EPSILON:
        arb_loss_to_retail_gain = -arb_edge / max(retail_edge, EPSILON)
    quote_selectivity_ratio = None
    if (
        arb_loss_to_retail_gain is not None
        and time_weighted_mean_fee is not None
        and time_weighted_mean_fee > EPSILON
    ):
        quote_selectivity_ratio = arb_loss_to_retail_gain / time_weighted_mean_fee

    return {
        "simulation_count": len(records),
        "mean_edge": _mean(mean_edges),
        "benchmark_mean_edge": _mean([record.benchmark_mean_edge for record in records]),
        "mean_edge_delta": _mean([record.mean_edge_delta for record in records]),
        "retail_volume_share": retail_volume_share,
        "arb_to_retail_volume_ratio": arb_to_retail_volume_ratio,
        "retail_edge": retail_edge,
        "arb_edge": arb_edge,
        "retail_flow_share": retail_flow_share,
        "arb_flow_share": arb_flow_share,
        "retail_gain_share": retail_gain_share,
        "arb_loss_share": arb_loss_share,
        "retail_trade_count": retail_trade_count,
        "arb_trade_count": arb_trade_count,
        "max_fee_jump": max_fee_jump,
        "time_weighted_bid_fee": time_weighted_bid_fee,
        "time_weighted_ask_fee": time_weighted_ask_fee,
        "time_weighted_mean_fee": time_weighted_mean_fee,
        "arb_loss_to_retail_gain": arb_loss_to_retail_gain,
        "quote_selectivity_ratio": quote_selectivity_ratio,
        "min_edge": min(mean_edges),
        "max_edge": max(mean_edges),
        "edge_stddev": _stddev(mean_edges),
    }


def _bucket_summary(
    records: list[ScorecardRecord],
    *,
    value_key: str,
    labels: tuple[str, ...],
) -> dict[str, dict[str, float | int | None]]:
    buckets: dict[str, list[ScorecardRecord]] = {label: [] for label in labels}
    if not records:
        return {label: _summarize_records([]) for label in labels}

    ranked = sorted(
        records, key=lambda record: (float(getattr(record, value_key)), record.seed)
    )
    bucket_count = len(labels)
    for index, record in enumerate(ranked):
        label = labels[min(bucket_count - 1, index * bucket_count // len(ranked))]
        buckets[label].append(record)

    return {
        label: _summarize_records(bucket_records)
        for label, bucket_records in buckets.items()
    }


def _grid_bucket_summary(
    records: list[ScorecardRecord],
    *,
    row_value_key: str,
    row_labels: tuple[str, ...],
    column_value_key: str,
    column_labels: tuple[str, ...],
) -> dict[str, dict[str, dict[str, float | int | None]]]:
    row_buckets = _assign_bucket_labels(records, value_key=row_value_key, labels=row_labels)
    column_buckets = _assign_bucket_labels(
        records,
        value_key=column_value_key,
        labels=column_labels,
    )
    grid: dict[str, dict[str, list[ScorecardRecord]]] = {
        row_label: {column_label: [] for column_label in column_labels}
        for row_label in row_labels
    }

    for record in records:
        grid[row_buckets[record.seed]][column_buckets[record.seed]].append(record)

    return {
        row_label: {
            column_label: _summarize_records(bucket_records)
            for column_label, bucket_records in column_map.items()
        }
        for row_label, column_map in grid.items()
    }


def _assign_bucket_labels(
    records: list[ScorecardRecord],
    *,
    value_key: str,
    labels: tuple[str, ...],
) -> dict[int, str]:
    if not records:
        return {}

    ranked = sorted(
        records, key=lambda record: (float(getattr(record, value_key)), record.seed)
    )
    bucket_count = len(labels)
    assignments: dict[int, str] = {}
    for index, record in enumerate(ranked):
        assignments[record.seed] = labels[
            min(bucket_count - 1, index * bucket_count // len(ranked))
        ]
    return assignments


def _resolve_edge_shares(
    *,
    retail_edge: float | None,
    arb_edge: float | None,
) -> tuple[float | None, float | None]:
    if retail_edge is None or arb_edge is None:
        return (None, None)

    retail_gain = max(float(retail_edge), 0.0)
    arb_loss = max(-float(arb_edge), 0.0)
    gross = retail_gain + arb_loss
    if gross <= EPSILON:
        return (None, None)
    return (retail_gain / gross, arb_loss / gross)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _stddev(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mean = _mean(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance)
