# combination_anchor_map

Seeded from `apr21-screen490-1431`.
This is the persistent cross-round synthesis surface for combination planning.
Append only durable positive anchors, compatibility/collision notes, and saturated failure modes that remain useful after a single round closes.

## Retained Context

- Official incumbent for the current `screen490` lane remains `screen_0001` at `485.92377070367183` mean edge.
- Best raw retained discard for the current `screen490` lane remains `screen_0002` / `burst-pivot` at `486.15826964779` mean edge.
- Use this note for scratch-round combination planning only; it does not change retained promotion semantics.

## Positive Anchors By Scaffold Layer Or Family

### Layer 4 burst / short-gap carry

- `screen_0002` / `burst-pivot`
  - Signal: `+0.23449894411817` mean edge vs incumbent; improved `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, `low_retail_mean_edge`, and `low_volatility_mean_edge`.
  - Compatibility: best used as one narrow gated admission inside a floor-preserving combination, not as another broad burst-carry clone.
  - Collision: low-decile weakened already, so do not stack with another burst/event relaxation or any safe-side reopen branch.

### Layer 1/3 observation basis and classifier evidence

- `OrthogonalObservationBasis`
  - Signal: `+0.07443633959468` mean edge vs incumbent while improving mean edge, leakage/selectivity, `time_weighted_mean_fee`, `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge` together.
  - Compatibility: cleanest upstream base for one downstream adjunct because it moves floor and retail together without touching layer 5/6 ownership.
  - Collision: do not spend more local OOB hazard-floor or participation-weight polish; `PersistenceShapedObservationBasis` and `PersistenceWeightedParticipationHazard` were exact phenotype replays.

- `BenignImpactPartitionClassifier`
  - Signal: mean edge was negative, but `low_decile_mean_edge` and retail improved enough to keep this as a real upstream diagnostic.
  - Compatibility: only worth combining with a branch that explicitly preserves the incumbent fee band and leakage band.
  - Collision: avoid pairing with burst relaxers, typed-export recapture changes, or anything else that lowers fees broadly.

### Layer 2 latent-state update

- `ImpactDominantDivergenceUpdateGate`
  - Signal: `+0.03454344988751` mean edge vs incumbent with better leakage/selectivity and slightly higher `time_weighted_mean_fee`.
  - Compatibility: usable only as a narrow secondary control next to a floor-positive anchor.
  - Collision: floor slices were weaker than both incumbent and OOB, so do not stack it with both OOB and the layer-5 inventory overlay in the same probe.

### Layer 5 toxic-side protection

- `InventoryToxicFloorOverlay` -> `RetailGuardedInventoryToxicOverlay` -> `RetailRecoveredInventoryOverlay`
  - Best signal: `RetailGuardedInventoryToxicOverlay` at `+0.04627622585633` mean edge vs incumbent.
  - Signal shape: slightly better mean edge, leakage/selectivity, `low_decile_mean_edge`, and `low_volatility_mean_edge`, but slight retail / low-retail giveback.
  - Compatibility: allow exactly one layer-5 exploit slot, ideally paired with an upstream retail-lifting anchor rather than another downstream control.
  - Collision: no new inventory latent, no centering-support magnitude change, no refill/calm-bonus coupling, and no more quiet-state taper clones.

## Support-Only Controls

- `ConsumedWidthRefillAmplificationVeto`
  - Signal: near no-op on mean edge, but slight `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge` lift.
  - Use: safe boundary veto if another anchor provides the actual upside.
  - Avoid: treating it as a primary anchor or pairing it with another refill/calm coupling edit.

- `PassiveRecaptureDecomposition`
  - Signal: near-frontier safety with baseline-like leakage/selectivity band.
  - Use: a compatibility reference for narrow downstream rewiring, not a positive anchor by itself.
  - Avoid: promoting it into another baseline-imitation loop without an explicit floor-lift thesis.

- `CappedLeakageRebateSuppression`
  - Signal: tiny support-only positive at `+0.010387304826565469` mean edge vs incumbent, with slight improvements in leakage/selectivity and all tracked floor slices.
  - Use: a narrow shared-rebate safety control when another branch supplies the primary upside.
  - Avoid: stacking it with OOB, burst admission, inventory overlays, or other weak positive anchors before a larger upstream anchor exists.

## Saturated Failure Modes

- Over-open leak basin
  - Signature: `quote_selectivity_ratio` drifts into roughly the high `20s` through `70+`, mean fee softens, arb leakage rises, and low-decile quality collapses.
  - Repeated sources: `ConfidenceDebtEstimator`, `ShockCarryInsuranceBudget`, `InventorySkewCenteringOverlay`, `RetailFloorGuardedInventoryOverlay`, `BasisOwnedClassifierExports`, `DualAnchorQuoteTopology`.

- Over-tightening basin
  - Signature: mean fee spikes or selectivity collapses too far, benign capture disappears, and most slices degrade together.
  - Repeated sources: `CarrySplitAssembler`, `BoundaryNormalizedStateLoop`, `AdverseExtensionFloorGuard`, `ElapsedGapHazardClassifier`; `ImpactSplitHazard` also leaned into this direction even though its arb metrics improved.

- Exact replay / no-op seam
  - Signature: source edits look new, but screen phenotype stays identical or effectively unchanged.
  - Repeated sources: `PersistenceShapedObservationBasis`, `PersistenceWeightedParticipationHazard`, `RecenterReleaseConfirmation`, `RatchetConfidenceVeto`.

- Saturated clone seam
  - Signature: a tiny anchor gets recopied locally until attribution gets worse and the batch collapses around one weak motif.
  - Repeated sources: inventory-overlay quiet-state tapers, typed-export ownership changes that touch recapture eligibility, direct latent/quote crossovers, standalone burst-label relaxations, and OOB-dependent short-gap or inventory recombinations.

- Near-frontier negative classifier controls
  - Signature: classifier-local evidence keeps the profile near the incumbent but moves floor slices slightly negative and fails to create a new anchor.
  - Repeated sources: `ClassifierExportSplit`, `TypedClassifierExportFirewall`, `RouteQualityCalmHazardPartition`.
  - Use: allow at most one softened follow-up when the interface remains classifier-local and does not feed global calm or recapture eligibility.

## Immediate Combination Rules

- Draft around one primary anchor and at most one secondary adjunct.
- Keep `OrthogonalObservationBasis` optional, not mandatory infrastructure for every probe.
- If `burst-pivot` is reused, pair it only with a floor-preserving partner and keep the burst admission narrow.
- If the layer-5 inventory overlay is reused, it must be the only layer-5/6 exploit slot in that probe.
- Pause OOB plus inventory and OOB plus short-gap combinations until a new non-OOB upstream anchor exists.
- Reject any draft that broadens safe-side opportunity, lowers fees across the board, or stacks several small safe signals with weak attribution.

## Productivity Rules For Future Rounds

- Stop spending whole rounds on scalar classifier terms that only add or damp `hazardObservation`; recent signed-impact and reversion-veto probes were either exact no-ops or over-open regressions.
- Treat support-only positives as stabilizers, not primary search ideas. `CappedLeakageRebateSuppression`, `ConsumedWidthRefillAmplificationVeto`, and `PassiveRecaptureDecomposition` should not be stacked together without a larger primary anchor.
- Do not recombine weak anchors across multiple downstream layers. Combination candidates should have one primary layer owner and at most one bounded secondary control.
- Require a fresh topology before Round 17 source work if the draft uses only incumbent-local vocabulary such as OOB, route/gap hazard, flow ownership, inventory overlay, burst admission, recenter release, or quiet-state refill.
- Favor interface-contract changes over coefficient changes:
  - separate adverse-selection protection evidence from benign-flow fee-capture evidence
  - keep estimator changes upstream of shared spread and side-specific protection
  - prove layer ownership in the plan before writing Solidity
- A candidate is not productive just because one diagnostic improves. Future scratch spends should define the expected movement in `mean_edge`, `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, and the three floor slices before probing.
