"""Tests for shared configuration."""

from typing import Any, cast

import pytest

import amm_sim_rs

from amm_competition.competition.config import (
    CANONICAL_FINAL_CONFIDENCE_SEEDS,
    BASELINE_SETTINGS,
    BASELINE_VARIANCE,
    CANONICAL_HOLDOUT_SEEDS,
    CANONICAL_SCREENING_SEEDS,
    STAGE_PRESETS,
    baseline_nominal_retail_rate,
    baseline_nominal_retail_size,
    baseline_nominal_sigma,
    build_base_config,
    build_config,
    build_stage_config,
    resolve_n_workers,
    resolve_stage_seed_block,
    validate_seed_blocks,
)


def test_build_base_config_matches_settings():
    cfg = build_base_config(seed=123)
    assert cfg.n_steps == BASELINE_SETTINGS.n_steps
    assert cfg.initial_price == BASELINE_SETTINGS.initial_price
    assert cfg.initial_x == BASELINE_SETTINGS.initial_x
    assert cfg.initial_y == BASELINE_SETTINGS.initial_y
    assert cfg.gbm_mu == BASELINE_SETTINGS.gbm_mu
    assert cfg.gbm_sigma == baseline_nominal_sigma()
    assert cfg.gbm_dt == BASELINE_SETTINGS.gbm_dt
    assert cfg.retail_arrival_rate == baseline_nominal_retail_rate()
    assert cfg.retail_mean_size == baseline_nominal_retail_size()
    assert cfg.retail_size_sigma == BASELINE_SETTINGS.retail_size_sigma
    assert cfg.retail_buy_prob == BASELINE_SETTINGS.retail_buy_prob
    assert cfg.seed == 123


def test_build_config_overrides_variable_params():
    cfg = build_config(
        seed=7,
        gbm_sigma=0.02,
        retail_arrival_rate=6.0,
        retail_mean_size=2.5,
        retail_size_sigma=0.9,
    )
    assert cfg.gbm_sigma == 0.02
    assert cfg.retail_arrival_rate == 6.0
    assert cfg.retail_mean_size == 2.5
    assert cfg.retail_size_sigma == 0.9
    assert cfg.initial_price == BASELINE_SETTINGS.initial_price
    assert cfg.initial_x == BASELINE_SETTINGS.initial_x
    assert cfg.initial_y == BASELINE_SETTINGS.initial_y


def test_variance_values_present():
    assert (
        BASELINE_VARIANCE.retail_mean_size_min < BASELINE_VARIANCE.retail_mean_size_max
    )
    assert (
        BASELINE_VARIANCE.retail_arrival_rate_min
        < BASELINE_VARIANCE.retail_arrival_rate_max
    )
    assert BASELINE_VARIANCE.gbm_sigma_min < BASELINE_VARIANCE.gbm_sigma_max


def test_simulation_config_requires_explicit_args():
    with pytest.raises(TypeError):
        cast(Any, amm_sim_rs.SimulationConfig)()


def test_resolve_n_workers_uses_bounded_cpu_default_when_env_unset(monkeypatch):
    monkeypatch.setattr(
        "amm_competition.competition.config.multiprocessing.cpu_count", lambda: 64
    )
    assert resolve_n_workers(env={}) == 8


@pytest.mark.parametrize("raw_value", ["abc", "0", "-2"])
def test_resolve_n_workers_rejects_invalid_env_values(raw_value: str):
    with pytest.raises(ValueError, match="N_WORKERS"):
        resolve_n_workers(env={"N_WORKERS": raw_value})


def test_canonical_seed_blocks_are_disjoint():
    validate_seed_blocks(CANONICAL_SCREENING_SEEDS, CANONICAL_HOLDOUT_SEEDS)
    validate_seed_blocks(CANONICAL_SCREENING_SEEDS, CANONICAL_FINAL_CONFIDENCE_SEEDS)
    validate_seed_blocks(CANONICAL_HOLDOUT_SEEDS, CANONICAL_FINAL_CONFIDENCE_SEEDS)


def test_validate_seed_blocks_rejects_overlap():
    with pytest.raises(ValueError, match="must not overlap"):
        validate_seed_blocks((1, 2, 3), (3, 4, 5))


def test_stage_presets_have_explicit_seed_blocks():
    for stage_name, preset in STAGE_PRESETS.items():
        seeds = resolve_stage_seed_block(stage_name)
        assert len(seeds) == preset.n_simulations
        assert len(set(seeds)) == len(seeds)


def test_non_smoke_stage_presets_gate_on_mean_edge():
    assert STAGE_PRESETS["smoke"].gate.min_mean_edge is None
    assert STAGE_PRESETS["validity_smoke"].gate.min_mean_edge is None
    for stage_name in (
        "fast_screen",
        "serious_screen",
        "pre_promotion",
        "final_confidence",
    ):
        assert STAGE_PRESETS[stage_name].gate.min_mean_edge == 0.0
    for stage_name in (
        "architecture_fast_screen",
        "mechanism_serious_screen",
        "holdout_confirmation",
        "final_confidence",
    ):
        assert STAGE_PRESETS[stage_name].gate.min_same_seed_mean_edge_delta == 0.0


def test_build_stage_config_uses_stage_preset_step_count():
    cfg = build_stage_config("smoke")
    assert cfg.n_steps == STAGE_PRESETS["smoke"].n_steps
    assert cfg.seed is None


def test_resolve_n_workers_uses_validated_env_override():
    assert resolve_n_workers(env={"N_WORKERS": "3"}) == 3


def test_resolve_n_workers_rejects_non_positive_env_override():
    with pytest.raises(ValueError, match="must be positive"):
        resolve_n_workers(env={"N_WORKERS": "0"})
