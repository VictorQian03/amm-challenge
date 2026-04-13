# Context Log

- Prior lane `apr12-screen480-1130` ended with one dominant failure cluster: `over_spiky_fee_surface`.
- Best raw prior improvement was small and came from a local hysteretic release tweak, not a wider pivot.
- Fresh lane `apr13-screen480-0907` was seeded before any code edits.
- `screen_0002` invalidated the fee-floor rewrite quickly: the branch materially cheapened the surface and produced severe arb leakage.
- `screen_0003` became the best fresh local signal: still non-promoting, but it improved the same calm-slice and arb diagnostics that mattered in the prior lane.
