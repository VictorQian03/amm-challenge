# Hypothesis Log

1. `fee-discipline-vol-accumulator-floor`
   - Expected effect: smoother protective repricing and less noisy calm release.
   - Result: invalidated by `screen_0002` after arb protection and weak slices collapsed.
2. `local-refine-concave-relief`
   - Expected effect: preserve protection while reducing overly broad cheap quoting.
   - Result: `screen_0003` improved the right diagnostics but did not clear promotion.
3. `anti-arb-side-markout-memory`
   - Expected effect: improve toxic-side defense without broad symmetric widening.
4. `weak-slice-exp-decay-envelope`
   - Expected effect: help calm weak slices with bounded, decaying relief rather than continuous rebates.
5. `structural-pivot-defensive-router-v2`
   - Expected effect: retry topology separation with a defensive default and stronger floor.
