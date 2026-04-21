"""Thin hill-climb harness primitives."""

from amm_competition.hill_climb.harness import (
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_STRATEGY_PATH,
    HillClimbHarness,
    HillClimbHarnessError,
)
from amm_competition.hill_climb.stages import HILL_CLIMB_STAGES, resolve_hill_climb_stage

__all__ = [
    "DEFAULT_ARTIFACT_ROOT",
    "DEFAULT_STRATEGY_PATH",
    "HILL_CLIMB_STAGES",
    "HillClimbHarness",
    "HillClimbHarnessError",
    "resolve_hill_climb_stage",
]
