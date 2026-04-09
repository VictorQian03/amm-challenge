# Hill-Climb Continuation: apr08-screen460-1819-cont1

## Objective

- Continue retained run `apr08-screen460-1819` from incumbent `screen_0001 @ 461.250395`.
- Use literature-guided refinements that preserve the current thresholded stress logic while testing more explicit inventory-aware quote skew.

## Literature Direction

- Dynamic AMM fee work indicates two distinct regimes: higher fees to deter arbitrageurs and lower fees to attract noise traders, with linear inventory-sensitive rules as a good practical approximation.
- Recent AMM fee simulation work argues for a threshold-style schedule: stable fees in normal conditions and materially higher protection only in very high volatility states.
- Inventory-based market-making control suggests quotes should shift with inventory around a reservation price rather than remain symmetric around the mid.

## Hypothesis Queue

- `h002-deadbanded-inventory-skew`
  - Add a deadbanded reservation-style side skew driven by divergence memory and recent price change, pushing fees further onto the toxic side and slightly easing the rebalancing side.
- `h003-stronger-inventory-skew`
  - If the first skew is positive, increase its amplitude modestly without changing the base threshold logic.
- `h004-deadbanded-skew-with-lighter-common-carry`
  - If the skew helps, trim a small amount of common one-sided spread carry and let the side-specific skew absorb more of the inventory response.

## Research Refs

- Uniswap v4 whitepaper
- Avellaneda-Stoikov inventory-based quoting
- Optimal Dynamic Fees in Automated Market Makers
- Optimal Fees for Liquidity Provision in Automated Market Makers
