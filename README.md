# AMM Fee Strategy Challenge

**https://ammchallenge.com**

Design dynamic fee strategies for a constant-product AMM. Your goal: maximize **edge**.

## Submission

Upload a `.sol` file containing a contract named `Strategy` that inherits from `AMMStrategyBase`.

Local results may diverge slightly from submission scores due to different RNG seeds. Run more simulations locally (`--simulations 1000`) to reduce variance and get closer to expected server results.

## The Simulation

Each simulation runs 10,000 steps. At each step:

1. **Price moves** — A fair price `p` evolves via geometric Brownian motion
2. **Arbitrageurs trade** — They push each AMM's spot price toward `p`, extracting profit
3. **Retail orders arrive** — Random buy/sell orders get routed optimally across AMMs

Your strategy competes against a **normalizer AMM** running fixed 30 bps fees. Both AMMs start with identical reserves (100 X, 10,000 Y at price 100).

### Price Process

The fair price follows GBM: `S(t+1) = S(t) · exp(-σ²/2 + σZ)` where `Z ~ N(0,1)`

- Drift `μ = 0` (no directional bias)
- Per-step volatility `σ ~ U[0.088%, 0.101%]` (varies across simulations)

### Retail Flow

Uninformed traders arrive via Poisson process:

- Arrival rate `λ ~ U[0.6, 1.0]` orders per step
- Order size `~ LogNormal(μ, σ=1.2)` with mean `~ U[19, 21]` in Y terms
- Direction: 50% buy, 50% sell

Retail flow splits optimally between AMMs based on fees—lower fees attract more volume.

## The Math

### Constant Product AMM

Reserves `(x, y)` satisfy `x * y = k`. The spot price is `y/x`. When the AMM sells Δx tokens:

```
Δy = y - k/(x - Δx)    (what trader pays)
```

Fees are taken on input: if fee is `f`, only `(1-f)` of the input affects reserves.

### Arbitrage

When spot price diverges from fair price `p`, arbitrageurs trade to close the gap. For fee `f` (fee-on-input), let `γ = 1 - f`:

- **Spot < fair** (AMM underprices X): Buy X from AMM. Optimal size: `Δx = x - √(k/(γ·p))`
- **Spot > fair** (AMM overprices X): Sell X to AMM. Optimal size: `Δx_in = (√(k·γ/p) - x) / γ`

Higher fees mean arbitrageurs need larger mispricings to profit, so your AMM stays "stale" longer—bad for edge.

### Order Routing

Retail orders split optimally across AMMs to equalize marginal prices post-trade. For two AMMs with fee rates `f₁, f₂`, let `γᵢ = 1 - fᵢ` and `Aᵢ = √(xᵢ γᵢ yᵢ)`. The optimal Y split is:

```
Δy₁ = (r(y₂ + γ₂Y) - y₁) / (γ₁ + rγ₂)    where r = A₁/A₂
```

Lower fees → larger `γ` → more flow. But the relationship is nonlinear—small fee differences can shift large fractions of volume.

### Edge

Edge measures profitability using the fair price at trade time:

```
Edge = Σ (amount_x × fair_price - amount_y)   for sells (AMM sells X)
     + Σ (amount_y - amount_x × fair_price)   for buys  (AMM buys X)
```

- **Retail trades**: Positive edge (you profit from the spread)
- **Arbitrage trades**: Negative edge (you lose to informed flow)

Good strategies maximize retail edge while minimizing arb losses.

## Why the Normalizer?

Without competition, setting 10% fees would appear profitable—you'd capture huge spreads on the few trades that still execute. The normalizer prevents this: if your fees are too high, retail routes to the 30 bps AMM and you get nothing.

The normalizer also means there's no "free lunch"—you can't beat 30 bps just by setting 29 bps. The optimal fee depends on market conditions.

## Writing a Strategy

**Start with `contracts/src/StarterStrategy.sol`** — a simple 50 bps fixed-fee strategy. Copy it, rename `getName()`, and modify the fee logic.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

contract Strategy is AMMStrategyBase {
    function afterInitialize(uint256 initialX, uint256 initialY)
        external override returns (uint256 bidFee, uint256 askFee);

    function afterSwap(TradeInfo calldata trade)
        external override returns (uint256 bidFee, uint256 askFee);

    function getName() external pure override returns (string memory);
}
```

The core mechanic: **you set a buy fee and a sell fee, and after every trade you can change what fees you're showing the market.**

`afterInitialize` is called once at simulation start — return your opening `(bidFee, askFee)`. Then `afterSwap` is called after every trade that hits your AMM. You see what just happened and return updated fees for the next trade.

| Field | Description |
|-------|-------------|
| `isBuy` | `true` if AMM bought X (trader sold X to you) |
| `amountX` | X traded (WAD precision, 1e18 = 1 unit) |
| `amountY` | Y traded |
| `timestamp` | Step number |
| `reserveX`, `reserveY` | Post-trade reserves |

Return fees in WAD: `30 * BPS` = 30 basis points. Max fee is 10%.

You get 32 storage slots (`slots[0..31]`) and helpers like `wmul`, `wdiv`, `sqrt`.

### Example: Widen After Big Trades

A simple strategy that bumps fees up after large trades and decays back to a base fee otherwise:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

contract Strategy is AMMStrategyBase {
    function afterInitialize(uint256, uint256) external override returns (uint256, uint256) {
        slots[0] = bpsToWad(30); // starting fee
        return (bpsToWad(30), bpsToWad(30));
    }

    function afterSwap(TradeInfo calldata trade) external override returns (uint256, uint256) {
        uint256 fee = slots[0];

        // Large trade relative to reserves? Widen the spread.
        uint256 tradeRatio = wdiv(trade.amountY, trade.reserveY);
        if (tradeRatio > WAD / 20) { // > 5% of reserves
            fee = clampFee(fee + bpsToWad(10));
        } else {
            // Decay back toward 30 bps
            uint256 base = bpsToWad(30);
            if (fee > base) fee = fee - bpsToWad(1);
        }

        slots[0] = fee;
        return (fee, fee);
    }

    function getName() external pure override returns (string memory) {
        return "Widen After Big Trades";
    }
}
```

## CLI

```bash
# Build the Rust engine
cd amm_sim_rs && pip install maturin && maturin develop --release && cd ..

# Install
pip install -e .

# Run 1000 simulations (default)
amm-match run my_strategy.sol

# Quick test
amm-match run my_strategy.sol --simulations 10

# Validate without running
amm-match validate my_strategy.sol
```

Output is your average edge across simulations. The 30 bps normalizer typically scores around 250-350 edge depending on market conditions.

## Thin Hill-Climb Harness

For retained local optimization, start from `contracts/src/StarterStrategy.sol` and use the thin harness instead of ad hoc notebook state.

```bash
uv run amm-match hill-climb eval --run-id apr21 --stage screen
uv run amm-match hill-climb probe --stage screen contracts/src/StarterStrategy.sol
uv run amm-match hill-climb status --run-id apr21
uv run amm-match hill-climb history --run-id apr21
uv run amm-match hill-climb compare-profiles --stage screen --run-id apr21 --baseline-eval-id screen_0001 --candidate-source contracts/src/StarterStrategy.sol
```

The harness keeps the eval layer strict and append-only, but it does not impose an idea-generation workflow.
On a fresh run, the first passing stage eval seeds that stage incumbent, so evaluating `contracts/src/StarterStrategy.sol` is the canonical local baseline seed.
Use `hill-climb probe` for worker-local branch scouting so worktree exploration does not create extra retained artifact directories.
Use the profile/failure-tag read surfaces to kill exhausted spines early and keep search entropy above simple incumbent-neighbor tweaks.
See [docs/hill_climb.md](docs/hill_climb.md) for the retained run layout, stage discipline, and search guidance.
