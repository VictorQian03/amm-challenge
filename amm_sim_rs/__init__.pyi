from typing import Dict, List, Tuple


class SimulationConfig:
    n_steps: int
    initial_price: float
    initial_x: float
    initial_y: float
    gbm_mu: float
    gbm_sigma: float
    gbm_dt: float
    retail_arrival_rate: float
    retail_mean_size: float
    retail_size_sigma: float
    retail_buy_prob: float
    seed: int | None

    def __init__(
        self,
        *,
        n_steps: int,
        initial_price: float,
        initial_x: float,
        initial_y: float,
        gbm_mu: float,
        gbm_sigma: float,
        gbm_dt: float,
        retail_arrival_rate: float,
        retail_mean_size: float,
        retail_size_sigma: float,
        retail_buy_prob: float,
        seed: int | None,
    ) -> None: ...


class StepResult:
    timestamp: int
    fair_price: float
    spot_prices: Dict[str, float]
    pnls: Dict[str, float]
    fees: Dict[str, Tuple[float, float]]


class BatchSimulationResult:
    seed: int
    strategies: List[str]
    pnl: Dict[str, float]
    edges: Dict[str, float]
    initial_fair_price: float
    initial_reserves: Dict[str, Tuple[float, float]]
    steps: List[StepResult]
    arb_volume_y: Dict[str, float]
    retail_volume_y: Dict[str, float]
    average_fees: Dict[str, Tuple[float, float]]
    retail_edge: Dict[str, float]
    arb_edge: Dict[str, float]
    retail_trade_count: Dict[str, int]
    arb_trade_count: Dict[str, int]
    max_fee_jump: Dict[str, float]
    time_weighted_fees: Dict[str, Tuple[float, float]]


class BatchResult:
    results: List[BatchSimulationResult]


def run_batch(
    strategy_a: List[int],
    strategy_b: List[int],
    configs: List[SimulationConfig],
    n_workers: int,
) -> BatchResult: ...
