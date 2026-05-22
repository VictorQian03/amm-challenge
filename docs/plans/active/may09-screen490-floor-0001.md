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

- [Rounds 01-05](may09-screen490-floor-0001-round01-05.md): current latest span; receives Rounds 1-5
- [Reference-layer oracle ablation memo](may09-screen490-floor-0001-oracle-ablation-memo.md): compact pointer to the authorized Reference.sol study
- [Reference oracle evidence cards](../../reference_oracle_evidence_cards.md): reusable oracle-transplant structure and distilled design rules

## Current Batch Discovery

- Latest populated span: `round01-05`
- Current write target: none pending search-frame decision
- Next span to create if this lane continues: `may09-screen490-floor-0001-round06-10.md`

## Continuation Convention

- Keep `docs/plans/active/may09-screen490-floor-0001.md` as the active run index; chunk files hold round narratives.
- Name each active chunk `docs/plans/active/<run_id>-roundSS-EE.md`, where `SS-EE` is the zero-padded inclusive 5-round span.
- Append new content to the highest listed span whose range still contains the latest round; create the next 5-round span only after the current one closes and this lane is intentionally continued.
- Keep scratch probe artifacts under `artifacts/scratch_probes/may09-screen490-floor-0001/roundN/`.

## Current State

- Active retained lane: `may09-screen490-floor-0001`
- Current incumbent: `screen_0001`
- Current incumbent mean edge: `487.01236396243195`
- Best raw non-promoted branch: none; seed is current best raw.
- Gap to breakout target from best raw: `2.98763603756805`
- Latest round: Round 5 used a scratch-only `WeakConsistencyEventFeasibilityMask` diagnostic seed pivot. It confirmed the parked WCEF frame remains stronger than the active floor seed on `screen`, but no retained eval was opened and any real WCEF-framed work should start as an explicit fresh run.

## Ready For Next Round

- Next round number: Round 6.
- Next write target: create `docs/plans/active/may09-screen490-floor-0001-round06-10.md` if this lane continues.
- Strategy source is reset to the retained seed snapshot `3f4bb9e4883515bf62bce866f36815402f6299c9e03b099e1f15f159acec4d9a`.
- Start with an explicit search-frame decision before worker source edits; Rounds 1-4 showed that new labels, upstream transforms, cut budgets, recenter gates, quote-mode selectors, trust gates, graph-credit labels, and attribution ledgers still fail when they flow through or starve the current hazard/protection/cut/fee consumer path.
- Do not request another floor-seed proposer pass unless it either changes seed/search frame, relaxes exactly one banned family with concrete kill thresholds, or introduces a consumer contract mechanically distinct from the current downstream paths. If WCEF becomes the implementation seed, start a fresh explicit WCEF-framed run instead of hiding the pivot inside `may09-screen490-floor-0001`.
- Retained eval should remain reserved for a scratch candidate that beats `screen_0001` or introduces a genuinely new floor-preserving consumer contract with materially better floor slices.
