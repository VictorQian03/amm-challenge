"""Shared configuration for baseline simulations and variance."""

from dataclasses import dataclass
import multiprocessing
import os
from typing import Mapping

import amm_sim_rs

from amm_competition.competition.match import HyperparameterVariance


@dataclass(frozen=True)
class BaselineSimulationSettings:
    n_simulations: int
    n_steps: int
    initial_price: float
    initial_x: float
    initial_y: float
    gbm_mu: float
    gbm_dt: float
    retail_buy_prob: float
    retail_size_sigma: float


@dataclass(frozen=True)
class StageGateThresholds:
    min_mean_edge: float | None = None
    min_retail_volume_share: float | None = None
    min_same_seed_mean_edge_delta: float | None = None


@dataclass(frozen=True)
class BenchmarkStagePreset:
    name: str
    n_simulations: int
    n_steps: int
    seed_block: str
    gate: StageGateThresholds


BASELINE_SETTINGS = BaselineSimulationSettings(
    n_simulations=1000,
    n_steps=10000,
    initial_price=100.0,
    initial_x=100.0,
    initial_y=10000.0,
    gbm_mu=0.0,
    gbm_dt=1.0,
    retail_buy_prob=0.5,
    retail_size_sigma=1.2,
)


BASELINE_VARIANCE = HyperparameterVariance(
    retail_mean_size_min=19.0,
    retail_mean_size_max=21.0,
    vary_retail_mean_size=True,
    retail_arrival_rate_min=0.6,
    retail_arrival_rate_max=1.0,
    vary_retail_arrival_rate=True,
    gbm_sigma_min=0.000882,
    gbm_sigma_max=0.001008,
    vary_gbm_sigma=True,
)

CANONICAL_SCREENING_SEEDS: tuple[int, ...] = tuple(range(256))
CANONICAL_HOLDOUT_SEEDS: tuple[int, ...] = tuple(range(1000, 3000))
CANONICAL_FINAL_CONFIDENCE_SEEDS: tuple[int, ...] = tuple(range(3000, 5000))

SEED_BLOCKS: Mapping[str, tuple[int, ...]] = {
    "screening": CANONICAL_SCREENING_SEEDS,
    "holdout": CANONICAL_HOLDOUT_SEEDS,
    "final_confidence": CANONICAL_FINAL_CONFIDENCE_SEEDS,
}

STAGE_PRESETS: Mapping[str, BenchmarkStagePreset] = {
    "smoke": BenchmarkStagePreset(
        name="smoke",
        n_simulations=16,
        n_steps=2000,
        seed_block="screening",
        gate=StageGateThresholds(),
    ),
    "fast_screen": BenchmarkStagePreset(
        name="fast_screen",
        n_simulations=64,
        n_steps=BASELINE_SETTINGS.n_steps,
        seed_block="screening",
        gate=StageGateThresholds(
            min_mean_edge=0.0,
        ),
    ),
    "serious_screen": BenchmarkStagePreset(
        name="serious_screen",
        n_simulations=256,
        n_steps=BASELINE_SETTINGS.n_steps,
        seed_block="screening",
        gate=StageGateThresholds(min_mean_edge=0.0),
    ),
    "pre_promotion": BenchmarkStagePreset(
        name="pre_promotion",
        n_simulations=512,
        n_steps=BASELINE_SETTINGS.n_steps,
        seed_block="holdout",
        gate=StageGateThresholds(
            min_mean_edge=0.0,
        ),
    ),
    "final_confidence": BenchmarkStagePreset(
        name="final_confidence",
        n_simulations=1000,
        n_steps=BASELINE_SETTINGS.n_steps,
        seed_block="final_confidence",
        gate=StageGateThresholds(
            min_mean_edge=0.0,
            min_same_seed_mean_edge_delta=0.0,
        ),
    ),
    "validity_smoke": BenchmarkStagePreset(
        name="validity_smoke",
        n_simulations=16,
        n_steps=2000,
        seed_block="screening",
        gate=StageGateThresholds(),
    ),
    "architecture_fast_screen": BenchmarkStagePreset(
        name="architecture_fast_screen",
        n_simulations=64,
        n_steps=BASELINE_SETTINGS.n_steps,
        seed_block="screening",
        gate=StageGateThresholds(
            min_mean_edge=0.0,
            min_same_seed_mean_edge_delta=0.0,
        ),
    ),
    "mechanism_serious_screen": BenchmarkStagePreset(
        name="mechanism_serious_screen",
        n_simulations=256,
        n_steps=BASELINE_SETTINGS.n_steps,
        seed_block="screening",
        gate=StageGateThresholds(
            min_mean_edge=0.0,
            min_same_seed_mean_edge_delta=0.0,
        ),
    ),
    "holdout_confirmation": BenchmarkStagePreset(
        name="holdout_confirmation",
        n_simulations=512,
        n_steps=BASELINE_SETTINGS.n_steps,
        seed_block="holdout",
        gate=StageGateThresholds(
            min_mean_edge=0.0,
            min_same_seed_mean_edge_delta=0.0,
        ),
    ),
}


def _default_n_workers() -> int:
    return min(8, multiprocessing.cpu_count())


def _midpoint(min_val: float, max_val: float) -> float:
    return (min_val + max_val) / 2


def validate_seed_blocks(
    screening_seeds: tuple[int, ...] = CANONICAL_SCREENING_SEEDS,
    holdout_seeds: tuple[int, ...] = CANONICAL_HOLDOUT_SEEDS,
) -> None:
    """Validate canonical seed blocks are explicit, unique, and disjoint."""
    if not screening_seeds or not holdout_seeds:
        raise ValueError("Screening and holdout seed blocks must both be non-empty")

    if len(set(screening_seeds)) != len(screening_seeds):
        raise ValueError("Screening seed block must not contain duplicates")
    if len(set(holdout_seeds)) != len(holdout_seeds):
        raise ValueError("Holdout seed block must not contain duplicates")

    overlap = set(screening_seeds).intersection(holdout_seeds)
    if overlap:
        raise ValueError(
            "Screening and holdout seed blocks must not overlap; "
            f"found overlap at seeds {sorted(overlap)[:5]}"
        )


validate_seed_blocks()


def baseline_nominal_sigma() -> float:
    return _midpoint(BASELINE_VARIANCE.gbm_sigma_min, BASELINE_VARIANCE.gbm_sigma_max)


def baseline_nominal_retail_rate() -> float:
    return _midpoint(
        BASELINE_VARIANCE.retail_arrival_rate_min,
        BASELINE_VARIANCE.retail_arrival_rate_max,
    )


def baseline_nominal_retail_size() -> float:
    return _midpoint(
        BASELINE_VARIANCE.retail_mean_size_min,
        BASELINE_VARIANCE.retail_mean_size_max,
    )


def resolve_n_workers(*, env: Mapping[str, str] | None = None) -> int:
    """Resolve worker count from environment or CPU count."""
    resolved_env = os.environ if env is None else env
    raw_value = resolved_env.get("N_WORKERS")
    if raw_value is None:
        return _default_n_workers()
    try:
        n_workers = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"N_WORKERS must be an integer, found {raw_value!r}") from exc
    if n_workers <= 0:
        raise ValueError(f"N_WORKERS must be positive, found {n_workers}")
    return n_workers


def build_base_config(*, seed: int | None) -> amm_sim_rs.SimulationConfig:
    """Build the canonical base SimulationConfig with explicit values."""
    return amm_sim_rs.SimulationConfig(
        n_steps=BASELINE_SETTINGS.n_steps,
        initial_price=BASELINE_SETTINGS.initial_price,
        initial_x=BASELINE_SETTINGS.initial_x,
        initial_y=BASELINE_SETTINGS.initial_y,
        gbm_mu=BASELINE_SETTINGS.gbm_mu,
        gbm_sigma=baseline_nominal_sigma(),
        gbm_dt=BASELINE_SETTINGS.gbm_dt,
        retail_arrival_rate=baseline_nominal_retail_rate(),
        retail_mean_size=baseline_nominal_retail_size(),
        retail_size_sigma=BASELINE_SETTINGS.retail_size_sigma,
        retail_buy_prob=BASELINE_SETTINGS.retail_buy_prob,
        seed=seed,
    )


def build_config(
    *,
    seed: int | None,
    gbm_sigma: float,
    retail_arrival_rate: float,
    retail_mean_size: float,
    retail_size_sigma: float,
) -> amm_sim_rs.SimulationConfig:
    """Build a SimulationConfig with explicit fields and variable parameters."""
    return amm_sim_rs.SimulationConfig(
        n_steps=BASELINE_SETTINGS.n_steps,
        initial_price=BASELINE_SETTINGS.initial_price,
        initial_x=BASELINE_SETTINGS.initial_x,
        initial_y=BASELINE_SETTINGS.initial_y,
        gbm_mu=BASELINE_SETTINGS.gbm_mu,
        gbm_sigma=gbm_sigma,
        gbm_dt=BASELINE_SETTINGS.gbm_dt,
        retail_arrival_rate=retail_arrival_rate,
        retail_mean_size=retail_mean_size,
        retail_size_sigma=retail_size_sigma,
        retail_buy_prob=BASELINE_SETTINGS.retail_buy_prob,
        seed=seed,
    )


def resolve_stage_preset(stage: str) -> BenchmarkStagePreset:
    """Return the benchmark stage preset for a known stage name."""
    try:
        return STAGE_PRESETS[stage]
    except KeyError as exc:
        raise ValueError(f"Unknown stage preset: {stage}") from exc


def resolve_stage_seed_block(stage: str) -> tuple[int, ...]:
    """Resolve the explicit canonical seed block for a stage preset."""
    preset = resolve_stage_preset(stage)
    seed_block = SEED_BLOCKS[preset.seed_block]
    if len(seed_block) < preset.n_simulations:
        raise ValueError(
            f"Seed block '{preset.seed_block}' only has {len(seed_block)} seeds, "
            f"but stage '{stage}' requires {preset.n_simulations}"
        )
    return seed_block[: preset.n_simulations]


def build_stage_config(stage: str) -> amm_sim_rs.SimulationConfig:
    """Build a base config for a benchmark stage preset."""
    preset = resolve_stage_preset(stage)
    return amm_sim_rs.SimulationConfig(
        n_steps=preset.n_steps,
        initial_price=BASELINE_SETTINGS.initial_price,
        initial_x=BASELINE_SETTINGS.initial_x,
        initial_y=BASELINE_SETTINGS.initial_y,
        gbm_mu=BASELINE_SETTINGS.gbm_mu,
        gbm_sigma=baseline_nominal_sigma(),
        gbm_dt=BASELINE_SETTINGS.gbm_dt,
        retail_arrival_rate=baseline_nominal_retail_rate(),
        retail_mean_size=baseline_nominal_retail_size(),
        retail_size_sigma=BASELINE_SETTINGS.retail_size_sigma,
        retail_buy_prob=BASELINE_SETTINGS.retail_buy_prob,
        seed=None,
    )
