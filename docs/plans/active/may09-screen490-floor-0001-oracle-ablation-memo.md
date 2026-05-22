# Reference-Layer Oracle Ablation Memo

Run: `may09-screen490-floor-0001`
Date: 2026-05-13
Oracle exception: the user explicitly authorized reading `contracts/src/Reference.sol` for this study.

This active-lane memo has been deduped into the reusable evidence-card format in [`docs/reference_oracle_evidence_cards.md`](../../reference_oracle_evidence_cards.md).

## Retained Facts

- Full Reference beat the active seed by roughly `+48..+53` edge across paired `screen`, `climb`, and `confirm` checks.
- Direct fair-mid, lambda-fee, low-base-fee, and side-shift transplants into current frontier consumers were strongly negative.
- Shadow oracle evidence routed to a single existing consumer still failed; namespace isolation alone did not fix the consumer contract.
- The only robust direct transplant in the prior study was `WeakConsistencyEventFeasibilityMask + ref_trade_tox_boost`, with confirm delta `+1.3047780456046092` over 512 seeds.
- Future reuse should stay at phenotype / metric / interface level unless the current task explicitly authorizes oracle access again.

## Artifact Policy

Raw oracle summaries, the protected oracle implementation, and implementation-level reproduction helpers are intentionally not committed. Keep future reuse at metric / phenotype / interface level unless the current task explicitly authorizes oracle access again.
