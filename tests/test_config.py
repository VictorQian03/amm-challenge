"""Tests for shared configuration."""

from typing import Any, cast

import pytest

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
    build_base_config,
    build_config,
    resolve_n_workers,
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
    assert BASELINE_VARIANCE.retail_mean_size_min < BASELINE_VARIANCE.retail_mean_size_max
    assert BASELINE_VARIANCE.retail_arrival_rate_min < BASELINE_VARIANCE.retail_arrival_rate_max
    assert BASELINE_VARIANCE.gbm_sigma_min < BASELINE_VARIANCE.gbm_sigma_max


def test_validate_seed_blocks_accepts_canonical_blocks():
    validate_seed_blocks(
        screening_seeds=CANONICAL_SCREENING_SEEDS,
        holdout_seeds=CANONICAL_HOLDOUT_SEEDS,
        final_confidence_seeds=CANONICAL_FINAL_CONFIDENCE_SEEDS,
    )


def test_validate_seed_blocks_rejects_overlap():
    with pytest.raises(ValueError, match="must not overlap"):
        validate_seed_blocks(
            screening_seeds=(1, 2, 3),
            holdout_seeds=(3, 4, 5),
            final_confidence_seeds=(6, 7, 8),
        )


def test_resolve_n_workers_validates_env_override():
    assert resolve_n_workers(env={"N_WORKERS": "3"}) == 3
    with pytest.raises(ValueError, match="must be an integer"):
        resolve_n_workers(env={"N_WORKERS": "three"})
    with pytest.raises(ValueError, match="must be positive"):
        resolve_n_workers(env={"N_WORKERS": "0"})


def test_simulation_config_requires_explicit_args():
    simulation_config_ctor = cast(Any, amm_sim_rs.SimulationConfig)
    with pytest.raises(TypeError):
        simulation_config_ctor()
