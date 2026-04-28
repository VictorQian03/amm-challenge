# combination_anchor_map

Seeded from `apr21-screen490-1431`.
This is the persistent cross-round synthesis surface for combination planning.
Append only durable positive anchors, compatibility/collision notes, and saturated failure modes that remain useful after a single round closes.

## Retained Context

- Official incumbent for the current `screen490` lane remains `screen_0001` at `485.92377070367183` mean edge.
- Best raw retained discard for the current `screen490` lane is now `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195` mean edge.
- Use this note for scratch-round combination planning only; it does not change retained promotion semantics.
- External phenotype calibration from the Apr 23 authorized oracle probe: the target space has much lower arb leakage/selectivity, lower mean fee, and materially higher floor slices than current local anchors.
- Treat oracle information only as phenotype evidence. Do not inspect or copy oracle/reference implementation details unless the active task explicitly authorizes it.

## Positive Anchors By Scaffold Layer Or Family

### Layer 4 burst / short-gap carry

- `screen_0002` / `burst-pivot`
  - Signal: `+0.23449894411817` mean edge vs incumbent; improved `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, `low_retail_mean_edge`, and `low_volatility_mean_edge`.
  - Compatibility: best used as one narrow gated admission inside a floor-preserving combination, not as another broad burst-carry clone.
  - Collision: low-decile weakened already, so do not stack with another burst/event relaxation or any safe-side reopen branch.

### Layer 1/3 observation basis and classifier evidence

- `screen_0005` / `RegimeSelectorStrongerFloor`
  - Signal: `+1.0885932587601133` mean edge vs incumbent; improved `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge` versus the incumbent and improved all tracked floor slices versus `screen_0004`.
  - Compatibility: current best raw anchor and measurement baseline; useful as a floor-preserving upstream/mid-scaffold selector when paired with a structurally different primary topology.
  - Collision: do not spend a full round on more regime-selector floor coefficients, mild fee release, burst-pivot bridge repair, or same-family fee-band polish. Round 20 showed broad release and burst bridging collapse floor slices.

- `screen_0003` / `InformationLiquiditySplitBusHardGuard`
  - Signal: `+0.29932807026233377` mean edge vs incumbent; improved `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge`.
  - Compatibility: strongest current upstream anchor because it separates liquidity demand from information stress without touching calm, recentering, refill, inventory, passive recapture, or layer 5/6 opportunity formulas.
  - Collision: do not turn it into another scalar hazard damper or pair it with broad fee compression; any follow-up should preserve the cleaner leakage/selectivity band and avoid support-only stacking.

- Scratch `SplitBusAdverseSelectionSideOnly`
  - Signal: `+0.31961900492069617` mean edge vs incumbent and `+0.020290934658362403` vs retained best raw while preserving the split-bus leakage/selectivity band and improving low-decile / low-retail slices.
  - Compatibility: secondary adjunct only; it extends the split bus into side-specific adverse-selection protection without direct shared-spread, calm, recentering, refill, inventory, passive recapture, or layer 5/6 opportunity changes.
  - Collision: same-family local refinement, not a new official anchor. Do not spend a round on more split-bus coefficient variants unless paired with a structurally different primary topology.

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
  - Repeated sources: `ConfidenceDebtEstimator`, `ShockCarryInsuranceBudget`, `InventorySkewCenteringOverlay`, `RetailFloorGuardedInventoryOverlay`, `BasisOwnedClassifierExports`, `DualAnchorQuoteTopology`, `ProfileTargetShadowNormalizer`.

- Over-tightening basin
  - Signature: mean fee spikes or selectivity collapses too far, benign capture disappears, and most slices degrade together.
  - Repeated sources: `CarrySplitAssembler`, `BoundaryNormalizedStateLoop`, `AdverseExtensionFloorGuard`, `ElapsedGapHazardClassifier`; `ImpactSplitHazard` also leaned into this direction even though its arb metrics improved.

- Exact replay / no-op seam
  - Signature: source edits look new, but screen phenotype stays identical or effectively unchanged.
  - Repeated sources: `PersistenceShapedObservationBasis`, `PersistenceWeightedParticipationHazard`, `RecenterReleaseConfirmation`, `RatchetConfidenceVeto`.

- Saturated clone seam
  - Signature: a tiny anchor gets recopied locally until attribution gets worse and the batch collapses around one weak motif.
  - Repeated sources: inventory-overlay quiet-state tapers, typed-export ownership changes that touch recapture eligibility, direct latent/quote crossovers, standalone burst-label relaxations, and OOB-dependent short-gap or inventory recombinations.

- Downstream floor-admission collapse
  - Signature: a final quote arbiter or safe-side service window appears structurally new, but it damages low-decile and low-retail floors while reopening leakage/selectivity.
  - Repeated sources: `FinalQuoteFloorArbiter`, `CapacityServiceWindow`.
  - Use: do not retry downstream admission without a stronger upstream floor-risk estimator; leave layer 6 alone for the immediate next round.

- Upstream estimator over-open collapse
  - Signature: an observation/state classifier looks structurally distinct, but attenuates protection too broadly and drives selectivity above roughly `30-65` with low-decile falling toward `210-265`.
  - Repeated sources: `ForecastErrorObservationGate`, `ImpactReconstructabilityEncoder`, `HorizonQuorumStateContract`, `AdverseOptionalityClassifier`.
  - Use: do not keep relabeling estimator confidence gates. Future upstream work needs an explicit protection-preserving boundary, not more trust/attenuation logic.

- Near-frontier negative classifier controls
  - Signature: classifier-local evidence keeps the profile near the incumbent but moves floor slices slightly negative and fails to create a new anchor.
  - Repeated sources: `ClassifierExportSplit`, `TypedClassifierExportFirewall`, `RouteQualityCalmHazardPartition`.
  - Use: allow at most one softened follow-up when the interface remains classifier-local and does not feed global calm or recapture eligibility.

## Immediate Combination Rules

- Draft around one primary anchor and at most one secondary adjunct.
- Keep `OrthogonalObservationBasis` optional, not mandatory infrastructure for every probe.
- Treat `InformationLiquiditySplitBusHardGuard` as the leading upstream anchor; follow-ups must explain how they preserve its leakage/selectivity improvement instead of merely increasing hazard or fees.
- Treat `screen_0005` / `RegimeSelectorStrongerFloor` as the current best raw anchor for measurement, but require the next batch to add a different primary topology instead of locally polishing that family.
- If `burst-pivot` is reused, pair it only with a floor-preserving partner and keep the burst admission narrow.
- If the layer-5 inventory overlay is reused, it must be the only layer-5/6 exploit slot in that probe.
- Pause OOB plus inventory and OOB plus short-gap combinations until a new non-OOB upstream anchor exists.
- Reject any draft that broadens safe-side opportunity, lowers fees across the board, or stacks several small safe signals with weak attribution.

## Productivity Rules For Future Rounds

- Use the three-role subagent pattern for probe-heavy batches as operator guidance, not harness state. Refer to hill_climb.md for more details. 
- Stop spending whole rounds on scalar classifier terms that only add or damp one hazard value; recent signed-impact and reversion-veto probes were either exact no-ops or over-open regressions.
- Treat support-only positives as stabilizers, not primary search ideas. `CappedLeakageRebateSuppression`, `ConsumedWidthRefillAmplificationVeto`, and `PassiveRecaptureDecomposition` should not be stacked together without a larger primary anchor.
- Do not recombine weak anchors across multiple downstream layers. Combination candidates should have one primary interface owner and at most one bounded secondary adjunct.
- Require at least one candidate outside incumbent vocabulary before the next source batch if every draft uses only OOB, route/gap hazard, flow ownership, inventory overlay, burst admission, recenter release, quiet-state refill, or scalar hazard damping.
- Favor interface-contract changes over coefficient changes:
  - separate adverse-selection protection evidence from benign-flow fee-capture evidence
  - keep upstream interpretation changes upstream of shared spread and side-specific protection
  - state allowed consumers and forbidden consumers before writing Solidity
  - prove layer ownership in the plan before source work
- Round 18 scratch lesson: public microstructure-inspired toxicity timing was structurally distinct but hurt low-decile in its first activation; a future retry needs a floor-preserving estimator selector, not stronger toxicity coefficients.
- Round 21 scratch lesson: downstream final-quote arbitration and safe-side service admission both collapsed floors; Round 22 should avoid layer 6 and avoid final-quote-only arbiters.
- Round 22 scratch lesson: upstream confidence/reconstructability/quorum classifiers collapsed even harder. Use external AMM/microstructure guidance before another batch and avoid trust-gate designs that attenuate protection.
