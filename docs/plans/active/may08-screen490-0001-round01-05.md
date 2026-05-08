# may08-screen490-0001 rounds 01-05

Run index: [may08-screen490-0001.md](may08-screen490-0001.md)

## Opening State

- Active retained lane: `may08-screen490-0001`.
- Retained seed: `screen_0001` / `seed-from-apr21-screen0008` at `488.03274719863765`.
- Breakout target: `490`.
- Source seed: Apr21 `screen_0008` / `weak-consistency-event-feasibility-mask`.
- Prior lane archive: [apr21-screen490-1431.md](../completed/apr21-screen490-1431.md).

## Seed Decision

The Apr21 lane saturated below target after Round 48. The May08 lane starts from the best measured Apr21 raw anchor rather than continuing to append scratch-only rounds to a historical lane.

## Carry-Forward Constraints

- Treat `WeakConsistencyEventFeasibilityMask` as the incumbent seed, not as permission for local event-feasibility residual coefficient tuning.
- Use `docs/combination_anchor_map.md` for durable saturated-basin and anchor lessons from Apr21.
- Keep retained writes serialized through `hill-climb eval`; use `hill-climb probe` for scratch scouting.
- Do not mutate Apr21 retained ledgers while continuing this lane.
