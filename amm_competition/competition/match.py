"""Match runner for baseline vs submission simulations using Rust engine."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping, Optional, Protocol, Sequence

import amm_sim_rs


@dataclass
class HyperparameterVariance:
    """Configuration for hyperparameter variance across simulations."""

    retail_mean_size_min: float
    retail_mean_size_max: float
    vary_retail_mean_size: bool

    retail_arrival_rate_min: float
    retail_arrival_rate_max: float
    vary_retail_arrival_rate: bool

    gbm_sigma_min: float
    gbm_sigma_max: float
    vary_gbm_sigma: bool


@dataclass
class LightweightStepResult:
    """Minimal step data for charting."""

    timestamp: int
    fair_price: float
    spot_prices: dict[str, float]
    pnls: dict[str, float]
    fees: dict[str, tuple[float, float]]


@dataclass
class LightweightSimResult:
    """Minimal simulation result for charting."""

    seed: int
    strategies: list[str]
    pnl: dict[str, Decimal]
    edges: dict[str, Decimal]
    initial_fair_price: float
    initial_reserves: dict[str, tuple[float, float]]
    steps: list[LightweightStepResult]
    arb_volume_y: dict[str, float]
    retail_volume_y: dict[str, float]
    average_fees: dict[str, tuple[float, float]]
    gbm_sigma: float
    retail_arrival_rate: float
    retail_mean_size: float
    retail_edge: dict[str, float] = field(default_factory=dict)
    arb_edge: dict[str, float] = field(default_factory=dict)
    retail_trade_count: dict[str, int] = field(default_factory=dict)
    arb_trade_count: dict[str, int] = field(default_factory=dict)
    max_fee_jump: dict[str, float] = field(default_factory=dict)
    time_weighted_fees: dict[str, tuple[float, float]] = field(default_factory=dict)


@dataclass
class MatchResult:
    """Result of a benchmark match."""

    strategy_a: str
    strategy_b: str
    wins_a: int
    wins_b: int
    draws: int
    total_pnl_a: Decimal
    total_pnl_b: Decimal
    total_edge_a: Decimal
    total_edge_b: Decimal
    simulation_results: list[LightweightSimResult] = field(default_factory=list)

    @property
    def winner(self) -> Optional[str]:
        if self.wins_a > self.wins_b:
            return self.strategy_a
        elif self.wins_b > self.wins_a:
            return self.strategy_b
        return None

    @property
    def total_games(self) -> int:
        return self.wins_a + self.wins_b + self.draws


class MatchStrategy(Protocol):
    """Minimal strategy contract required by the Rust match runner."""

    @property
    def bytecode(self) -> bytes: ...

    def get_name(self) -> str: ...


class MatchRunner:
    """Runs matches using Rust simulation engine."""

    def __init__(
        self,
        *,
        n_simulations: int,
        config: amm_sim_rs.SimulationConfig,
        n_workers: int,
        variance: HyperparameterVariance,
        seed_block: Optional[Sequence[int]] = None,
    ):
        self.n_simulations = n_simulations
        self.base_config = config
        self.n_workers = n_workers
        self.variance = variance
        self.seed_block = self._resolve_seed_block(seed_block)

    def _resolve_seed_block(
        self, seed_block: Optional[Sequence[int]]
    ) -> Optional[tuple[int, ...]]:
        if seed_block is None:
            return None

        resolved = tuple(int(seed) for seed in seed_block)
        if len(resolved) != self.n_simulations:
            raise ValueError(
                "Explicit seed_block length must match n_simulations "
                f"({len(resolved)} != {self.n_simulations})"
            )
        if len(set(resolved)) != len(resolved):
            raise ValueError("Explicit seed_block must not contain duplicate seeds")
        return resolved

    def _build_configs(self) -> list[amm_sim_rs.SimulationConfig]:
        """Build simulation configs with optional variance."""
        import numpy as np

        configs = []
        seeds = (
            self.seed_block
            if self.seed_block is not None
            else tuple(range(self.n_simulations))
        )
        for seed in seeds:
            rng = np.random.default_rng(seed=seed)

            retail_mean_size = (
                rng.uniform(
                    self.variance.retail_mean_size_min,
                    self.variance.retail_mean_size_max,
                )
                if self.variance.vary_retail_mean_size
                else self.base_config.retail_mean_size
            )
            retail_arrival_rate = (
                rng.uniform(
                    self.variance.retail_arrival_rate_min,
                    self.variance.retail_arrival_rate_max,
                )
                if self.variance.vary_retail_arrival_rate
                else self.base_config.retail_arrival_rate
            )
            gbm_sigma = (
                rng.uniform(self.variance.gbm_sigma_min, self.variance.gbm_sigma_max)
                if self.variance.vary_gbm_sigma
                else self.base_config.gbm_sigma
            )

            cfg = amm_sim_rs.SimulationConfig(
                n_steps=self.base_config.n_steps,
                initial_price=self.base_config.initial_price,
                initial_x=self.base_config.initial_x,
                initial_y=self.base_config.initial_y,
                gbm_mu=self.base_config.gbm_mu,
                gbm_sigma=gbm_sigma,
                gbm_dt=self.base_config.gbm_dt,
                retail_arrival_rate=retail_arrival_rate,
                retail_mean_size=retail_mean_size,
                retail_size_sigma=self.base_config.retail_size_sigma,
                retail_buy_prob=self.base_config.retail_buy_prob,
                seed=seed,
            )
            configs.append(cfg)
        return configs

    def run_match(
        self,
        strategy_a: MatchStrategy,
        strategy_b: MatchStrategy,
        store_results: bool = False,
    ) -> MatchResult:
        """Run a complete match between two strategies."""
        name_a = strategy_a.get_name()
        name_b = strategy_b.get_name()

        # Build configs
        configs = self._build_configs()

        # Run simulations in Rust
        batch_result = amm_sim_rs.run_batch(
            list(strategy_a.bytecode),
            list(strategy_b.bytecode),
            configs,
            self.n_workers,
        )

        # Process results
        wins_a = 0
        wins_b = 0
        draws = 0
        total_pnl_a = Decimal("0")
        total_pnl_b = Decimal("0")
        total_edge_a = Decimal("0")
        total_edge_b = Decimal("0")
        simulation_results = []
        configs_by_seed: dict[int, amm_sim_rs.SimulationConfig] = {}
        for cfg in configs:
            if cfg.seed is None:
                raise RuntimeError("Simulation config is missing a seed")
            configs_by_seed[int(cfg.seed)] = cfg

        for rust_result in batch_result.results:
            # Get PnL values using fixed positional keys from Rust
            pnl_a = _required_result_value(
                rust_result.pnl, "submission", field_name="pnl"
            )
            pnl_b = _required_result_value(
                rust_result.pnl, "normalizer", field_name="pnl"
            )
            edge_a = _required_result_value(
                rust_result.edges, "submission", field_name="edges"
            )
            edge_b = _required_result_value(
                rust_result.edges, "normalizer", field_name="edges"
            )

            total_pnl_a += Decimal(str(pnl_a))
            total_pnl_b += Decimal(str(pnl_b))
            total_edge_a += Decimal(str(edge_a))
            total_edge_b += Decimal(str(edge_b))

            if edge_a > edge_b:
                wins_a += 1
            elif edge_b > edge_a:
                wins_b += 1
            else:
                draws += 1

            if store_results:
                # Convert Rust result to Python dataclass
                steps = [
                    LightweightStepResult(
                        timestamp=s.timestamp,
                        fair_price=s.fair_price,
                        spot_prices=s.spot_prices,
                        pnls=s.pnls,
                        fees=s.fees,
                    )
                    for s in rust_result.steps
                ]
                sim_config = configs_by_seed.get(int(rust_result.seed))
                if sim_config is None:
                    raise RuntimeError(
                        f"Missing simulation config for stored result seed {rust_result.seed}"
                    )

                sim_result = LightweightSimResult(
                    seed=rust_result.seed,
                    strategies=list(rust_result.strategies),
                    pnl={k: Decimal(str(v)) for k, v in rust_result.pnl.items()},
                    edges={k: Decimal(str(v)) for k, v in rust_result.edges.items()},
                    initial_fair_price=rust_result.initial_fair_price,
                    initial_reserves=dict(rust_result.initial_reserves),
                    steps=steps,
                    arb_volume_y=dict(rust_result.arb_volume_y),
                    retail_volume_y=dict(rust_result.retail_volume_y),
                    average_fees=dict(rust_result.average_fees),
                    gbm_sigma=sim_config.gbm_sigma,
                    retail_arrival_rate=sim_config.retail_arrival_rate,
                    retail_mean_size=sim_config.retail_mean_size,
                    retail_edge=_required_float_mapping(
                        rust_result,
                        "retail_edge",
                    ),
                    arb_edge=_required_float_mapping(
                        rust_result,
                        "arb_edge",
                    ),
                    retail_trade_count=_required_int_mapping(
                        rust_result,
                        "retail_trade_count",
                    ),
                    arb_trade_count=_required_int_mapping(
                        rust_result,
                        "arb_trade_count",
                    ),
                    max_fee_jump=_required_float_mapping(
                        rust_result,
                        "max_fee_jump",
                    ),
                    time_weighted_fees=_required_fee_pair_mapping(
                        rust_result,
                        "time_weighted_fees",
                    ),
                )
                simulation_results.append(sim_result)

        return MatchResult(
            strategy_a=name_a,
            strategy_b=name_b,
            wins_a=wins_a,
            wins_b=wins_b,
            draws=draws,
            total_pnl_a=total_pnl_a,
            total_pnl_b=total_pnl_b,
            total_edge_a=total_edge_a,
            total_edge_b=total_edge_b,
            simulation_results=simulation_results,
        )


def _required_result_value(
    mapping: dict[str, float], key: str, *, field_name: str
) -> float:
    if key not in mapping:
        raise RuntimeError(f"Rust result missing required key '{key}' in {field_name}")
    return float(mapping[key])


def _required_result_mapping(result: object, field_name: str) -> Mapping[str, object]:
    if not hasattr(result, field_name):
        raise RuntimeError(f"Rust result missing required field: {field_name}")
    mapping = getattr(result, field_name)
    if not isinstance(mapping, Mapping):
        raise RuntimeError(f"Rust result field {field_name} must be a mapping")
    return mapping


def _required_float_mapping(result: object, field_name: str) -> dict[str, float]:
    values: dict[str, float] = {}
    for key, value in _required_result_mapping(result, field_name).items():
        if not isinstance(value, int | float):
            raise RuntimeError(
                f"Rust result field {field_name} must contain numeric values"
            )
        values[str(key)] = float(value)
    return values


def _required_int_mapping(result: object, field_name: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for key, value in _required_result_mapping(result, field_name).items():
        if not isinstance(value, int):
            raise RuntimeError(
                f"Rust result field {field_name} must contain integer values"
            )
        values[str(key)] = value
    return values


def _required_fee_pair_mapping(
    result: object, field_name: str
) -> dict[str, tuple[float, float]]:
    pairs: dict[str, tuple[float, float]] = {}
    for key, value in _required_result_mapping(result, field_name).items():
        if not isinstance(value, tuple) or len(value) != 2:
            raise RuntimeError(f"Rust result field {field_name} must contain fee pairs")
        first, second = value
        if not isinstance(first, int | float) or not isinstance(second, int | float):
            raise RuntimeError(
                f"Rust result field {field_name} must contain numeric fee pairs"
            )
        pairs[str(key)] = (float(first), float(second))
    return pairs
