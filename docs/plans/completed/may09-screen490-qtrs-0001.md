# may09-screen490-qtrs-0001

This root note is the completed index for the fresh retained screen490 lane seeded from the Apr21 tail-state anchor after the May08 WCEF-seeded lane saturated below target.

## Run Context

- Run id: `may09-screen490-qtrs-0001`
- Retained lane status: `historical`
- Global hill-climb index status: `historical`
- Seed eval: `screen_0001`
- Seed label: `seed-from-apr21-screen0007`
- Strategy: `QuantileTailRiskSketch`
- Mean edge: `487.54341156295743`
- Breakout target: `490`
- Seed source: `artifacts/hill_climb/apr21-screen490-1431/snapshots/7fce3149b3de21ffd8894fb9593eb111219b2b99bdbc67cbe8eef1847436f28c.sol`
- Prior parked lane: `docs/plans/completed/may08-screen490-0001.md`
- Successor active lane: `docs/plans/active/may09-screen490-floor-0001.md`

## Round Index

- [Rounds 01-05](may09-screen490-qtrs-0001-round01-05.md): closed span covering Rounds 1-5 and the saturation decision

## Current Batch Discovery

- Latest populated span: `round01-05`
- Current write target: none; this run is closed.
- Next span to create after this one closes: none unless the user explicitly reopens this historical lane.

## Continuation Convention

- Keep `docs/plans/completed/may09-screen490-qtrs-0001.md` as the completed run index; chunk files hold round narratives.
- Name each completed chunk `docs/plans/completed/<run_id>-roundSS-EE.md`, where `SS-EE` is the zero-padded inclusive 5-round span.
- Do not append new rounds to this run. Use `docs/plans/active/may09-screen490-floor-0001.md` for continuation work.
- Keep scratch probe artifacts under `artifacts/scratch_probes/may09-screen490-qtrs-0001/roundN/`.

## Current State

- Active retained lane: none; this run is closed.
- Current incumbent: `screen_0001`
- Current incumbent mean edge: `487.54341156295743`
- Best raw non-promoted branch: `screen_0004` / `majorization-risk-vector-filter` at `487.7232131981818`
- Gap to breakout target from best raw: `2.2767868018182185`
- Latest round: Round 5 recorded QTRS-local saturation before source work; the current local frame could not defend six non-replay candidates under the expanded Round 1-4 exclusion set.
- Follow-up: `may09-screen490-floor-0001` starts a fresh seed-frame lane from Apr21 `screen_0005` / `RegimeSelectorStrongerFloor`.
