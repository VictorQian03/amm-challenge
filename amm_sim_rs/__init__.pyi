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

class LightweightStepResult:
    timestamp: int
    fair_price: float
    spot_prices: dict[str, float]
    pnls: dict[str, float]
    fees: dict[str, tuple[float, float]]

class LightweightSimResult:
    seed: int
    strategies: list[str]
    pnl: dict[str, float]
    edges: dict[str, float]
    initial_fair_price: float
    initial_reserves: dict[str, tuple[float, float]]
    steps: list[LightweightStepResult]
    arb_volume_y: dict[str, float]
    retail_volume_y: dict[str, float]
    average_fees: dict[str, tuple[float, float]]
    gbm_sigma: float
    retail_arrival_rate: float
    retail_mean_size: float
    retail_edge: dict[str, float]
    arb_edge: dict[str, float]
    retail_trade_count: dict[str, int]
    arb_trade_count: dict[str, int]
    max_fee_jump: dict[str, float]
    time_weighted_fees: dict[str, tuple[float, float]]

    def winner(self) -> str | None: ...

class BatchSimulationResult:
    results: list[LightweightSimResult]
    strategies: list[str]

    def win_counts(self) -> tuple[int, int, int]: ...
    def total_pnl(self) -> tuple[float, float]: ...
    def overall_winner(self) -> str | None: ...
    def __len__(self) -> int: ...

def run_single(
    submission_bytecode: list[int] | bytes,
    baseline_bytecode: list[int] | bytes,
    config: SimulationConfig,
) -> LightweightSimResult: ...
def run_batch(
    submission_bytecode: list[int] | bytes,
    baseline_bytecode: list[int] | bytes,
    configs: list[SimulationConfig],
    n_workers: int = 0,
) -> BatchSimulationResult: ...
