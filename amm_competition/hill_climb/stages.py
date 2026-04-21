"""Thin canonical stage presets for hill-climb evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from amm_competition.competition.config import (
    CANONICAL_FINAL_CONFIDENCE_SEEDS,
    CANONICAL_HOLDOUT_SEEDS,
    CANONICAL_SCREENING_SEEDS,
    resolve_n_workers,
)
from amm_competition.competition.match import MatchRunner
from amm_competition.competition.config import BASELINE_SETTINGS, BASELINE_VARIANCE
from amm_competition.competition.config import (
    baseline_nominal_retail_rate,
    baseline_nominal_retail_size,
    baseline_nominal_sigma,
)
import amm_sim_rs


@dataclass(frozen=True)
class HillClimbStage:
    """A fixed evaluation stage for comparison discipline."""

    name: str
    n_simulations: int
    seed_block: tuple[int, ...]
    description: str
    min_mean_edge: float | None
    max_arb_loss_to_retail_gain: float | None = None
    max_fee_jump: float | None = None


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
        description="Quick compile/runtime sanity check on competition-length sims.",
        min_mean_edge=None,
    ),
    "prescreen": HillClimbStage(
        name="prescreen",
        n_simulations=12,
        seed_block=_stage_seed_block(CANONICAL_SCREENING_SEEDS, 12),
        description="Cheap viability filter for risky pivots before full screening.",
        min_mean_edge=0.0,
        max_arb_loss_to_retail_gain=0.20,
    ),
    "screen": HillClimbStage(
        name="screen",
        n_simulations=32,
        seed_block=_stage_seed_block(CANONICAL_SCREENING_SEEDS, 32),
        description="Canonical fixed-seed screening stage.",
        min_mean_edge=0.0,
    ),
    "climb": HillClimbStage(
        name="climb",
        n_simulations=128,
        seed_block=_stage_seed_block(CANONICAL_SCREENING_SEEDS, 128),
        description="Larger screening block for confident incumbent replacement.",
        min_mean_edge=0.0,
    ),
    "confirm": HillClimbStage(
        name="confirm",
        n_simulations=512,
        seed_block=_stage_seed_block(CANONICAL_HOLDOUT_SEEDS, 512),
        description="Disjoint holdout confirmation before promotion.",
        min_mean_edge=0.0,
    ),
    "final": HillClimbStage(
        name="final",
        n_simulations=1000,
        seed_block=_stage_seed_block(CANONICAL_FINAL_CONFIDENCE_SEEDS, 1000),
        description="Largest local confidence stage on final-confidence seeds.",
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
