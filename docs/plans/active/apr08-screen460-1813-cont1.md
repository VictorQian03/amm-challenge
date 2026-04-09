# Hill-Climb Continuation: apr08-screen460-1813-cont1

## Objective

- Continue retained run `apr08-screen460-1813` from incumbent `screen_0001 @ 461.212266`.
- Follow the current harness guidance by refining the active directional-burst-skew family before any new pivot.

## Refinement Queue

- `h002-quiet-divergence-release`
  - Add a narrow post-recenter release path that only decays stale divergence memory after long quiet gaps.
- `h003-more-directional-burst-split`
  - Push a bit more of the above-threshold event surcharge onto the toxic side and slightly reduce the shared burst carry.
- `h004-lighter-shared-flow-tax`
  - Keep the current directional burst split but reduce the shared one-sided flow tax another step to test whether common spread drag is still too high.

## Decision Notes

- The current winner already came from reducing shared one-sided taxation and keeping only a lighter divergence-sensitive toxic-side overlay.
- Worker `w01` suggests a quiet divergence release path is directionally plausible, but its standalone variant underperformed the current winner.
- The next refinements should remain small and inspectable so the run history can distinguish whether residual drag is coming from stale divergence memory, shared burst carry, or shared one-sided flow taxation.
