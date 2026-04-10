# AMM Dynamic Fee Memo

## Question

Which AMM fee-design ideas still look underexplored for the current `screen` frontier in `contracts/src/Strategy.sol`, given the fresh retained seed at `473.616393` and a new breakout gate of `480`?

## Sources And Credibility

- High: Uniswap v4 whitepaper sections on hook-managed dynamic fees and volatility-shifting fee examples.
- High: Campbell, Bergault, Milionis, Nutz, "Optimal Fees for Liquidity Provision in Automated Market Makers" (arXiv 2025).
- High: Cartea, Drissi, Monga, "Decentralised Finance and Automated Market Making: Predictable Loss and Optimal Liquidity Provision" (arXiv / SIAM JFM).
- High: Milionis, Wan, Adams, "FLAIR: A Metric for Liquidity Provider Competitiveness in Automated Market Makers" (arXiv 2023).
- Medium: OpenGradient dynamic-fee research note on volatility and markout-sensitive fee updates.

## Findings

1. Threshold-like fee schedules remain plausible.
   The 2025 optimal-fees paper finds fees should stay competitive in normal conditions and rise materially only in very high volatility, which supports a sharper regime switch instead of broad linear carry everywhere.

2. Fast price-risk and slower regime-risk should stay separate.
   Uniswap v4 explicitly frames dynamic fees and volatility-sensitive hooks as composable overlays, which supports preserving a fast transient jump signal rather than forcing slow hazard memory to do all the work.

3. Adverse selection and competitiveness matter in different ways.
   FLAIR separates toxicity from competitiveness, which argues against solving low-edge buckets with a blanket higher fee floor; selective repricing is more consistent with the theory than broad spread drag.

4. Mild skew or leaning can be useful when the state is directional but not toxic.
   The predictable-loss paper shows skewed liquidity can outperform symmetric provision when drift is present. In this single-file strategy, the closest analog is a bounded reserve-skew or side-tie-breaker overlay, not a global asymmetry.

5. Markout-sensitive overlays are directionally supported but should stay simple.
   The OpenGradient note is lower-credibility than the papers, but it reinforces a practical implementation detail: a recent-price-jump memory can widen quickly after adverse moves and decay quickly when conditions calm down.

## Implications For This Round

- Avoid another broad quiet-band rebate family unless it is paired with a cleaner toxicity discriminator.
- Spend mutation budget on one of three axes: fast price-jump memory, bounded inventory lean, or a clearer continuation-vs-recovery phase switch.
- Prefer minimal state additions that remap existing signals over wholesale coefficient churn.

## Recommended Worker Mapping

1. `w01-price-jump-memory`
   Add a fast transient jump-memory sidecar and use it to keep calm shared carry lighter while still widening after repeated jumps.
2. `w02-inventory-lean-lite`
   Add a bounded reserve-skew tie-breaker that only matters when hazard and flow pressure are not already screaming toxic.
3. `w03-healing-disagreement`
   Reward recovery only when price extension and signed flow disagree, instead of offering broad calm-mode relief.
4. `w04-phase-fee-synth`
   Translate the threshold-fee evidence into one minimal phase-transition surface on top of the current incumbent.
