# AMM Fee Strategy Challenge

**https://ammchallenge.com**

Design dynamic fee strategies for a constant-product AMM. Your goal: maximize **edge**.

## Submission

Upload a `.sol` file containing a contract named `Strategy` that inherits from `AMMStrategyBase`.

Local results may diverge slightly from submission scores due to different RNG seeds. Run more simulations locally (`--simulations 1000`) to reduce variance and get closer to expected server results.

## Canonical Docs

- [docs/agent_harness_guide.md](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/agent_harness_guide.md): agent read order, retained-lane analysis, and evidence gathering
- [docs/hill_climb_loop.md](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/hill_climb_loop.md): harness contract, artifact schema, stage gates, and stop policy
- [docs/codex_idea_generation_prompt.md](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/codex_idea_generation_prompt.md): fresh-batch prompt contract and anti-replay rules

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

**Start with `contracts/src/StarterStrategy.sol`** and copy it into `contracts/src/Strategy.sol`. The hill-climb harness treats `contracts/src/Strategy.sol` as the only active edit path for a run. `contracts/src/StarterStrategy.sol` is the starter template, `contracts/src/VanillaStrategy.sol` is the fixed-fee normalizer fixture, and `contracts/src/Reference.sol` is a protected benchmark fixture that should only be opened when the user explicitly authorizes access.

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
# One-shot local setup
./scripts/setup_local.sh

# Repo-local commands should use uv so agents do not depend on shell activation.

# Run a candidate directly
uv run amm-match run contracts/src/Strategy.sol

# Quick direct test
uv run amm-match run contracts/src/Strategy.sol --simulations 10

# Validate without running
uv run amm-match validate contracts/src/Strategy.sol

# Record a hill-climb eval
uv run amm-match hill-climb eval contracts/src/Strategy.sol --run-id mar26 --stage screen --label baseline

# Register a branch hypothesis so planning surfaces stay meaningful
uv run amm-match hill-climb set-hypothesis --run-id mar26 --hypothesis-id anti-arb-01 --title "Anti-arb branch" --rationale "Reduce toxic-flow leakage without fee spikes" --expected-effect "Improve arb discipline while preserving screen mean_edge" --mutation-family anti-arb --target-metrics arb_loss_to_retail_gain=-0.03 --hard-guardrails max_fee_jump=0.005 --expected-failure-mode arb_leak_regression

# Inspect the current stage incumbent
uv run amm-match hill-climb status --run-id mar26 --stage screen --json

# Inspect the run with machine-readable output
uv run amm-match hill-climb analyze-run --run-id mar26 --json

# Compare two stored evals on the same stage
uv run amm-match hill-climb compare-profiles --run-id mar26 --stage screen --baseline-eval-id screen_0001 --candidate-eval-id screen_0002

# Restore the current stage incumbent into the active file
uv run amm-match hill-climb pull-best --run-id mar26 --stage screen --destination contracts/src/Strategy.sol

```

Output is your average edge across simulations. The 30 bps normalizer typically scores around 250-350 edge depending on market conditions.

## Hill-Climb Loop

This repo now uses a formal hill-climbing harness inspired by single-file autoresearch loops:

- the competition mechanics and evaluator stay fixed,
- agents mutate one active strategy file at a time at `contracts/src/Strategy.sol`,
- every eval runs against the built-in 30 bps normalizer,
- the deciding metric is `mean_edge` subject to stage gates and an uncertainty-aware promotion margin,
- every stage keeps competition-length simulations (`10000` steps),
- only the number of simulations changes by stage.

Stage presets:

- `smoke`: 8 sims
- `prescreen`: 12 sims with extra arb-leak / fee-jump guardrails for risky pivots
- `screen`: 32 sims
- `climb`: 128 sims
- `confirm`: 512 sims
- `final`: 1000 sims

Artifacts are written to `artifacts/hill_climb/<run_id>/` with a versioned `run.json`, resumable `state.json`, append-only results, shared content-addressed source snapshots under `snapshots/`, and stage incumbents. Keep one active run under `artifacts/hill_climb/` and one smoke sanity run under `artifacts/hill_climb_smoke/`; delete probe, compare, and superseded baseline runs after their conclusions are folded back into the active lane. Legacy `evaluations/` trees, stale manifests, duplicate eval IDs, and obsolete continuity files are unsupported in active runs and should not be retained there.

Decision rule:

- a stage must clear its gate before it can seed or replace an incumbent,
- the first gate-passing result for a stage is `seed`,
- later results are `keep` only if `delta_vs_incumbent` clears the promotion margin derived from candidate and incumbent uncertainty,
- otherwise the result is `discard`.

Agent-facing read surfaces:

- `status`, `history`, `show-eval`, `show-hypothesis`, `summarize-run`, `analyze-run`, `compare-profiles`, and `pull-best` all support `--json`.
- `status`, `history`, `show-eval`, `show-hypothesis`, `summarize-run`, `analyze-run`, and `compare-profiles` support `--read-only` so old runs remain inspectable after protected-surface drift.
- `status` now surfaces the official incumbent, the strongest raw survivor, the latest eval, and the current loop guidance separately so retained-lane triage does not collapse those roles together.
- `analyze-run` planning outputs depend on maintained hypothesis records; update branches with `set-hypothesis` if you want decomposition coverage, batch-diversity checks, structural recommendations, `intent_coverage`, `portfolio_gaps`, `family_scoreboard`, `layer_scoreboard`, `portfolio_bank`, and `recommended_next_batch` to reflect the real search portfolio.
- `analyze-run` now exposes failure clusters, layer/topology diversity checks, phenotype intent coverage, mutation-family and primary-layer risk scoreboards, notebook-style findings/dead ends, a screen-stage `portfolio_bank` of near-frontier planning anchors, the screen-stage official incumbent, and recommended anchor eval ids instead of only raw frontier ids.
- each retained lane also renders a derived notebook under `artifacts/hill_climb/<run_id>/notebook/` with `findings.md`, `dead_ends.md`, and `search_risk.md`; these are convenience outputs rebuilt from canonical ledgers, not authoritative state.
- `docs/agent_harness_guide.md` is the canonical map for active-run CLI usage, historical retained-lane analysis, and research / idea-generation artifact read order.

See `docs/hill_climb_loop.md` for the canonical artifact schema, progression policy, and stop rules.

## Protected Mechanics Hooks

This repo ships with versioned git hooks under `.githooks/` and a protected-path manifest in `.competition-protected-paths`.

- `./scripts/setup_local.sh` installs the local environment and sets `core.hooksPath=.githooks`
- `pre-commit` and `pre-push` block protected mechanics edits whether they are staged or still dirty in the working tree
- `uv run amm-match hill-climb eval` also refuses to run against a dirty protected surface, and retained runs pin a protected-surface fingerprint in `run.json`
- intentional edits can still be made by setting `ALLOW_COMPETITION_MECHANICS_EDIT=1`
