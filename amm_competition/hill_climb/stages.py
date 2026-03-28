"""Canonical stage presets for mean-edge hill climbing."""

from __future__ import annotations

from dataclasses import dataclass

import amm_sim_rs

from amm_competition.competition.config import (
    BASELINE_SETTINGS,
    BASELINE_VARIANCE,
    CANONICAL_FINAL_CONFIDENCE_SEEDS,
    CANONICAL_HOLDOUT_SEEDS,
    CANONICAL_SCREENING_SEEDS,
    baseline_nominal_retail_rate,
    baseline_nominal_retail_size,
    baseline_nominal_sigma,
    resolve_n_workers,
)
from amm_competition.competition.match import MatchRunner


@dataclass(frozen=True)
class HillClimbStage:
    """A research stage with fixed competition settings and explicit seeds."""

    name: str
    n_simulations: int
    seed_block: tuple[int, ...]
    description: str
    min_mean_edge: float | None


def _stage_seed_block(
    seed_source: tuple[int, ...], n_simulations: int
) -> tuple[int, ...]:
    if len(seed_source) < n_simulations:
        raise ValueError(
            f"Seed source only has {len(seed_source)} seeds for {n_simulations} simulations"
        )
    return seed_source[:n_simulations]


HILL_CLIMB_STAGES: dict[str, HillClimbStage] = {
    "smoke": HillClimbStage(
        name="smoke",
        n_simulations=8,
        seed_block=_stage_seed_block(CANONICAL_SCREENING_SEEDS, 8),
        description="Quick compile/runtime sanity check on competition-length simulations.",
        min_mean_edge=None,
    ),
    "screen": HillClimbStage(
        name="screen",
        n_simulations=32,
        seed_block=_stage_seed_block(CANONICAL_SCREENING_SEEDS, 32),
        description="Fast mean-edge screening on canonical screening seeds.",
        min_mean_edge=0.0,
    ),
    "climb": HillClimbStage(
        name="climb",
        n_simulations=128,
        seed_block=_stage_seed_block(CANONICAL_SCREENING_SEEDS, 128),
        description="Primary hill-climbing stage on a larger fixed screening block.",
        min_mean_edge=0.0,
    ),
    "confirm": HillClimbStage(
        name="confirm",
        n_simulations=512,
        seed_block=_stage_seed_block(CANONICAL_HOLDOUT_SEEDS, 512),
        description="Holdout confirmation before final submission selection.",
        min_mean_edge=0.0,
    ),
    "final": HillClimbStage(
        name="final",
        n_simulations=1000,
        seed_block=_stage_seed_block(CANONICAL_FINAL_CONFIDENCE_SEEDS, 1000),
        description="Full competition-aligned local confidence run.",
        min_mean_edge=0.0,
    ),
}


def resolve_hill_climb_stage(stage_name: str) -> HillClimbStage:
    """Return a known hill-climb stage or fail loudly."""
    try:
        return HILL_CLIMB_STAGES[stage_name]
    except KeyError as exc:
        raise ValueError(f"Unknown hill-climb stage: {stage_name}") from exc


def build_stage_config() -> amm_sim_rs.SimulationConfig:
    """Build the immutable competition-aligned simulation config."""
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
        seed=None,
    )


def build_stage_runner(stage_name: str, *, n_workers: int | None = None) -> MatchRunner:
    """Build a MatchRunner for the requested hill-climb stage."""
    stage = resolve_hill_climb_stage(stage_name)
    return MatchRunner(
        n_simulations=stage.n_simulations,
        config=build_stage_config(),
        n_workers=resolve_n_workers() if n_workers is None else n_workers,
        variance=BASELINE_VARIANCE,
        seed_block=stage.seed_block,
    )
