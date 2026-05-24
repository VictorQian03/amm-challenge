# may09-screen490-floor-0001 Rounds 06-10

This chunk records outcome-level evidence for the continued floor-seed lane. Raw scratch trees and oracle implementation details are intentionally not committed; the canonical retained ledger and reusable evidence-card boundary remain the durable sources.

## State Entering The Span

- Active retained incumbent: `screen_0001` / `LatentStateQuoteEngine` at `487.01236396243195`.
- Retained best raw at the start of Round 6: `screen_0004` / `OracleTradeToxCoef6500` at `489.8573894977019`.
- Breakout target: `490`.
- Retained eval rule: spend a canonical eval only for a scratch candidate that beats live best raw or establishes a materially different floor-risk owner.

## Round 6: Trade-Aligned Toxicity Continuation

- Boundary: no oracle implementation access; work continued only from live retained state and distilled prior findings.
- Tested local activation, cap, split, size-tranche, and post-cut-shield variants around the best-raw source.
- Outcome: no scratch candidate beat `screen_0004`; `TradeToxSplit7200` was the nearest miss at `489.8164946601735` and traded lower mean for small leakage/selectivity and floor movement.
- Decision: no retained eval. Do not spend another local trade-tox routing or coefficient variation without a new owner/consumer contract.

## Rounds 7-9: Authorized Oracle Study

- Boundary: the user explicitly authorized oracle access for these study rounds only. The default boundary after this span is no oracle implementation access without fresh authorization.
- Durable result: the retained ledger already captures the positive best-raw branch at `screen_0004`; `docs/reference_oracle_evidence_cards.md` owns the reusable interface-level lesson.
- Outcome: subsequent authorized consumer-contract experiments did not clear smoke/screen gates and reinforced the `oracle-consumer-contract-gap` conclusion.
- Cleanup: implementation-level generators, raw summaries, and candidate trees remain local-only or were removed; they are not repository evidence.
- Decision: do not reopen oracle-inspired sidecar, admission, release-veto, tail-assembly, escrow, or telemetry variants on this base without a new consumer contract and explicit oracle authorization.

## Round 10: No-Oracle OOD Additive Holds

- Boundary: no oracle implementation access; proposals used external mechanism vocabulary and the live `screen_0004` base only.
- Tested add-only holds from predicate, capability, antichain, wavelet, robust-statistics, morphology, sketch, and sequential-evidence families.
- Outcome: all variants failed smoke with the same floor-collapse/selectivity phenotype and none earned screen or retained eval.
- Decision: additive hold variants are saturated on this base. A productive continuation requires a fresh search frame, one explicitly relaxed family with kill thresholds, or a non-additive primary owner.

## Span Decision

- The canonical lane remains active because Round 11 found a later best-raw branch, recorded in `may09-screen490-floor-0001-round11-15.md`.
- Retain only canonical `run.json`, `results.jsonl`, referenced snapshots, and these compact decisions for Rounds 6-10.
- Do not regenerate or stage the removed scratch trees as part of normal continuation.
