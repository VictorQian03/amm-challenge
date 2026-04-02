# AMM Dynamic Fee Memo

## Question

What external AMM design ideas are most compatible with improving the current `LatentStateIncumbentGapAwareV4` screen incumbent without abandoning the repo's single-file hill-climb loop?

## Sources And Credibility

- High: Uniswap v4 whitepaper on hook-managed dynamic fees and volatility-shifting fee examples.
- Medium-High: Cao, Kogan, Tsoukalas, Falk, "A Structural Model of Automated Market Making" (SSRN working paper).
- Medium: Lebedeva et al., "Dynamic Fee for Reducing Impermanent Loss in Decentralized Exchanges" (arXiv / ICBC 2025).

## Findings

1. Volatility-sensitive fees are directionally supported.
   The structural model paper argues fixed fees are inefficient and that volatility-sensitive fee schedules outperform fixed fees in empirical tests. This supports keeping a separate risk memory for realized markout risk instead of using only raw trade size.

2. Asymmetric adaptive fees are directionally supported.
   The ICBC 2025 paper explicitly studies asymmetric block-adaptive and deal-adaptive fees and reports better LP outcomes than fixed-fee baselines. That lines up with side-specific stale-side widening and with rebates only on inventory-restoring flow.

3. Fast transient toxicity and slower regime risk should not be conflated.
   Uniswap v4's dynamic-fee hook framing is generic, but it reinforces the implementation pattern: detect a local event, adjust fees dynamically, and avoid forcing one monolithic fee surface to carry every signal. For this repo, that implies a short-lived clustered-flow pulse should stay distinct from slower cooldown or size memory.

## Implications For This Repo

- Favor one focused overlay at a time on top of the current `V4` incumbent.
- Separate transient pulse logic from persistent cooldown logic.
- Keep any restorative rebate tightly gated by quiet conditions; prior broad recapture ideas underperformed.
- Prefer directional changes over symmetric moderate-shock widening, because the current `V4` already captures a strong defensive baseline.

## Recommended Next Batch

1. `price-vol-memory`: add a fast-decay price-jump memory that lifts common fees after repeated markout-heavy moves but fades faster than cooldown after idle gaps.
2. `idle-sidecar-recapture`: rebate only the non-toxic side when `gap`, `cooldown`, and `eventSignal` all indicate calm conditions.
3. `inventory-lean-lite`: apply reserve-skew only as a bounded tie-breaker in calm-to-moderate states, not as a broad cross-surface overlay.

## Round Context

- Fresh retained run: `apr01-screen420-2134`
- Fresh screen baseline: `screen_0001 seed @ 428.250099`
- Current recommendation: promote the baseline incumbent to `climb` before attempting broader mutations.
