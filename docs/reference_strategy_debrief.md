# Reference Strategy Debrief

Use `contracts/src/Reference.sol` as an architectural benchmark, not a porting target.

## Core Lesson

The reference is strong because it separates the job into layers instead of stacking one
more overlay onto a single additive fee surface.

Use this four-layer decomposition:

- `state estimation`: what latent market condition is being inferred
- `risk budget`: what should widen for protection, and why
- `opportunity budget`: when cheapening is earned, temporary, and bounded
- `quote map`: how those budgets become bid/ask fees

## Incumbent Trap

The incumbent already has useful signals, but most recent branches stayed inside the same
spine:

- another signal on the same surface
- another release path
- another smoother retune

That looks diverse in labels but not in topology. It is why the retained runs keep finding
near-replays and the same failure cluster.

## Hypothesis Contract

Before coding, each hypothesis should say:

- primary layer changed
- one layer intentionally held fixed
- hidden coupling being removed
- why this is not just a coefficient retune
- expected upside
- expected failure signature

## Batch Rule

- Cover at least three different primary layers in a new batch.
- Include at least one true topology pivot.
- If two survivors are near-replays, pivot layers before retuning again.
