# Reference Strategy Debrief

## Goal

Use `contracts/src/Reference.sol` as an architectural benchmark, not a porting target.
The objective is to move future strategy design and hypothesis generation toward the same
problem decomposition while keeping implementation choices original and high level.

## What The Reference Gets Right

`Reference.sol` is stronger than the incumbent because it does not treat quoting as one
large additive fee surface with many overlapping overlays.
It first estimates a small set of latent market states, then maps those states into
separate quote components.

The important pattern is:

1. Estimate market state.
2. Translate that state into shared spread, side-specific protection, and conditional
   opportunity spend.
3. Recombine those components into the final bid/ask surface.

That decomposition matters more than any specific coefficient choice.

## The Architectural Gap In The Incumbent

The incumbent already has useful state, but it still behaves like a feature stack.
New ideas mostly arrive as local overlays on top of an existing additive surface:

- one more toxicity term
- one more directional adjustment
- one more release mechanism
- one more tail clamp

That makes the search look diverse while staying inside the same underlying topology.
The result is visible in the retained run history:

- multiple branches improved slices slightly but were near-replays of one another
- supposedly orthogonal pivots still cheapened the surface too broadly
- the harness kept rediscovering the same failure cluster: `over_spiky_fee_surface`

The core issue is not just tuning. The abstraction layer of the search is too low.

## Better Problem Decomposition

Future designs should reason in four layers.

### 1. State Estimation

Model a compact latent view of the market.
Examples of state categories:

- fair-value anchor
- short-horizon stress or hazard
- directional pressure or one-sidedness
- calm or recapture capacity
- divergence between traded price and anchor

The key requirement is that each state should have a clear semantic job.
If two states both exist to justify fee widening, the decomposition is already muddy.

### 2. Risk Budget

Build the part of the quote that exists to defend against adverse selection.
This should answer:

- when should both sides widen together?
- when should only one side pay for risk?
- what evidence says the state is dangerous rather than merely active?

This is where the incumbent most often collapses back into a monolithic surface.

### 3. Opportunity Budget

Treat competitive cheapening as a separate budget, not as the absence of protection.
Opportunity spend should be gated, temporary, and explicitly justified by benign state.

That is the deeper lesson from the reference design:
cheapness should be earned under calm conditions, not appear automatically whenever risk
signals are slightly lower.

### 4. Quote Map

Only after the first three layers are defined should they be translated into bid/ask fees.
The mapping should stay interpretable:

- shared spread
- side-specific surcharge
- side-specific rebate or release

If a new idea cannot say which of those three objects it changes, it is probably still
living at the wrong abstraction level.

## What This Means For Future Ideas

Good future hypotheses should not start from:

- "add another signal"
- "smooth the current term"
- "lower average fees a bit"
- "retry the same branch with gentler coefficients"

They should start from:

- which layer is wrong?
- which coupling is currently hidden?
- which budget is being spent by the wrong mechanism?
- which state transition should happen earlier, later, or not at all?

The best ideas will usually change one layer while holding the other three mostly fixed.
That makes the search more legible and prevents semantically narrow batches.

## Minimal Harness Fixes

The harness does not need a large rewrite.
It needs a thinner idea-generation contract.

### Required For Each Hypothesis

Every new hypothesis should declare:

- primary layer changed: `state`, `risk_budget`, `opportunity_budget`, or `quote_map`
- layer held fixed on purpose
- hidden coupling being removed
- why the idea is not just a coefficient retune of the incumbent spine
- expected win condition
- expected failure signature

### Required For Each New Batch

Each batch should cover at least three distinct decomposition targets.
A batch with five ideas that all keep the same quote topology is not diverse, even if the
labels differ.

At least one branch per batch should be a true topology branch, meaning it changes how the
quote is assembled rather than how one existing term is tuned.

### Local-Optimum Rule

If two surviving branches are near-replays, or a batch produces multiple same-spine misses,
the next batch should pivot layers instead of retuning coefficients again.

That is the minimal change with the highest leverage.

## Design Questions To Ask Before Coding

Before writing Solidity, answer these questions in words:

1. What market state is the strategy trying to estimate?
2. Which part of the quote is protection, and which part is competitive spend?
3. Under what evidence can the strategy safely become cheaper?
4. What single hidden coupling in the incumbent is this idea trying to break?
5. Why is this branch structurally different from the last surviving branch?

If those answers are weak, the idea is not ready for implementation.
