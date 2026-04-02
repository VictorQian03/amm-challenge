# PRD

## Goal

Generate bounded, literature-informed mutation ideas that can plausibly improve the current `screen` incumbent without widening the implementation surface.

## Acceptance Criteria

- Ideas must fit inside `contracts/src/Strategy.sol`.
- Ideas must be evaluable through the canonical hill-climb CLI.
- Ideas must be separable enough that one retained eval can isolate each hypothesis.

## Ranked Candidate Themes

1. Separate transient toxicity from slower price-volatility risk.
2. Narrow quiet-side rebates instead of lowering broad calm carry.
3. Use inventory skew only as a tie-breaker, not a primary fee driver.
