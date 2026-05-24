# may09-screen490-floor-0001

This root note is the active index for the fresh retained screen490 lane seeded from the Apr21 floor-preserving selector anchor after the May09 QTRS-local lane saturated below target.

## Run Context

- Run id: `may09-screen490-floor-0001`
- Retained lane status: `active`
- Global hill-climb index status: `active`
- Seed eval: `screen_0001`
- Seed label: `seed-from-apr21-screen0005`
- Strategy: `LatentStateQuoteEngine` / `RegimeSelectorStrongerFloor`
- Mean edge: `487.01236396243195`
- Breakout target: `490`
- Seed source: `artifacts/hill_climb/apr21-screen490-1431/snapshots/3f4bb9e4883515bf62bce866f36815402f6299c9e03b099e1f15f159acec4d9a.sol`
- Prior saturated lane: `docs/plans/completed/may09-screen490-qtrs-0001.md`

## Round Index

- [Rounds 01-05](may09-screen490-floor-0001-round01-05.md): closed span; receives Rounds 1-5
- [Rounds 06-10](may09-screen490-floor-0001-round06-10.md): closed span; receives Rounds 6-10
- [Rounds 11-15](may09-screen490-floor-0001-round11-15.md): current latest span; receives Rounds 11-15
- [Reference-layer oracle ablation memo](may09-screen490-floor-0001-oracle-ablation-memo.md): compact pointer to the authorized Reference.sol study
- [Reference oracle evidence cards](../../reference_oracle_evidence_cards.md): reusable oracle-transplant structure and distilled design rules

## Current Batch Discovery

- Latest populated span: `round11-15`
- Current write target: none pending search-frame decision
- Current oracle boundary: default back to no oracle implementation access unless explicitly authorized; Rounds 7-9 were a closed, explicitly authorized study.
- Next span to create after Round 15 if this lane continues: `may09-screen490-floor-0001-round16-20.md`

## Continuation Convention

- Keep `docs/plans/active/may09-screen490-floor-0001.md` as the active run index; chunk files hold round narratives.
- Name each active chunk `docs/plans/active/<run_id>-roundSS-EE.md`, where `SS-EE` is the zero-padded inclusive 5-round span.
- Append new content to the highest listed span whose range still contains the latest round; create the next 5-round span only after the current one closes and this lane is intentionally continued.
- Keep scratch probe artifacts under `artifacts/scratch_probes/may09-screen490-floor-0001/roundN/`.

## Current State

- Active retained lane: `may09-screen490-floor-0001`
- Current incumbent: `screen_0001`
- Current incumbent mean edge: `487.01236396243195`
- Best raw non-promoted branch: `screen_0005` / `flow-dir-risk-280` / `FlowDirectionalRisk280`
- Best raw mean edge: `490.75833078204124`
- Breakout margin from best raw: `+0.7583307820412446`
- Latest round: Round 11 ran a 100-variant scratch hyperparameter sweep from `screen_0004` plus near-frontier bases. `FlowDirectionalRisk280` survived smoke, screen, climb, and confirm with better mean and named floor slices, then received canonical retained eval as `screen_0005`.

## Ready For Next Round

- Next round number: Round 12.
- Next write target: append to `docs/plans/active/may09-screen490-floor-0001-round11-15.md` if this lane intentionally continues.
- Strategy source is intentionally set to the retained best-raw branch `FlowDirectionalRisk280` for continuation from `screen_0005`.
- Do not spend another pure flow-directional-risk coefficient polish, trade-tox local tweak, no-cut sidecar owner, admission-gating branch, tail-slope branch, lambda release-veto branch, escrow branch, stale-side/null-routing branch, telemetry-owner rewrite, or add-only OOD hold on this base unless the user explicitly relaxes that banned family with kill thresholds.
- Retained eval should remain reserved for a scratch candidate that beats live best raw `screen_0005` or introduces a genuinely new floor-risk owner with materially better named floor slices.
