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

### Layer 1/4 curve geometry and shared-spread floor

- Scratch `ConstantProductCurvatureGuard`
  - Signal: `+0.48478819025184` mean edge vs incumbent with better `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge`, but still `-0.60380506850828` versus `screen_0005`.
  - Compatibility: useful as bounded curve-geometry evidence for shared-spread protection when a separate primary topology supplies the main upside.
  - Collision: not strong enough as a standalone retained candidate. Do not spend a round on curvature coefficients alone or combine it with broad fee-rent / LVR-floor tuning.

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

### Layer 2/3 floor-risk partition

- Scratch `RetailFloorFirstStatePartition`
  - Signal: `+1.0762424413238136` mean edge vs incumbent with much better `arb_loss_to_retail_gain=0.08387766865965202`, `quote_selectivity_ratio=16.081469460894738`, `low_retail_mean_edge=416.32788458867`, and `low_volatility_mean_edge=464.1427325479601`, but still `-0.012350817436299621` versus `screen_0005` and with elevated `time_weighted_mean_fee=0.005215796284264762`.
  - Compatibility: useful as a positive floor-first partition anchor when a distinct primary topology can preserve the leakage/selectivity lift without fee overcharge.
  - Collision: do not locally polish the floor partition or stack it with another classifier/protection-only control. Its next use needs a different primary interface or a fee-band-preserving constraint that does not create release/opportunity behavior.

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

Keep this section extensible. Add a new failure mode when repeated probes share a profile signature that is not well described by the current vocabulary; prefer a precise phenotype name over forcing evidence into `over_open_leak`, `over_tighten_clamp`, `frontier_neighbor`, or `crossover_regression`. A useful entry names the signature, repeated sources, and the critique question that should block similar future ideas before source work.

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

- Post-spread fee-rent collapse
  - Signature: a public microstructure-inspired fee-rent idea adds global or asymmetric rent after the incumbent has already formed shared spread / side protection, but fails to protect floors and often reopens selectivity.
  - Repeated sources: `VolatilityIndexedBaseSpread`, `InventoryDirectionFeeSlope`, `TwoClockRiskRent`.
  - Use: do not retry simple volatility-indexed base fees, inventory-direction surcharges, or dual-clock rent overlays.

- Strict LVR floor no-op
  - Signature: a narrow AMM/LVR floor proxy avoids over-open collapse and preserves the incumbent band, but is effectively phenotype-identical to the incumbent and remains below `screen_0005`.
  - Repeated sources: `LVRProxySpreadFloor`.
  - Use: do not coefficient-tune the strict LVR floor alone. Only revisit if a distinct primary topology supplies new floor-risk evidence before the layer-4 floor proxy consumes it.

- Protection-starvation basin
  - Signature: a protection-only classifier or geometry signal avoids over-open leakage but pushes fees/protection high enough that mean edge and all floor slices collapse.
  - Repeated sources: `BatchClearingLatencyPressure`, `ReserveBandExhaustionClassifier`, `VolumeBucketImbalanceLattice`.
  - Use: do not retry broad latency-pressure or reserve-exhaustion classifiers unless the interface includes an explicit cap that preserves retail capture and keeps the incumbent fee band interpretable.

- Temporal-clearing overprotection basin
  - Signature: a discrete-time, latency, collision, or batch-pressure interface looks structurally distinct, but the classification feeds hazard/shared protection too broadly: fees rise above the incumbent band, selectivity climbs, and all tracked floor slices break.
  - Repeated sources: `BatchClearingLatencyPressure`, `BatchCollisionObservationSplitter`, `DiscreteClearingClockState`.
  - Use: do not retry temporal clearing or batch-pressure classifiers as a primary scoring idea unless the interface has a hard no-overcharge boundary and can preserve benign retail capture before touching hazard or shared spread.

- Aged-premium release basin
  - Signature: a layer 2 evidence lifetime or layer 4 premium cap appears to target high-fee floor protection, but instead releases too much downstream behavior: `quote_selectivity_ratio` around `70`, `time_weighted_mean_fee` around `0.00361`, and low-decile / low-retail floors collapse.
  - Repeated sources: `AgingEvidenceLedgerWithPremiumBudgetCap`, `AgingEvidencePostCutPremium`.
  - Use: do not retry the Round 27 high-fee fix by adding another cap to floor-risk or evidence-age terms. Future fee-band preservation needs an interface that cannot feed opportunity cuts, inventory, final quote selection, or shared fee compression.

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

- Use the optional proposer / critic / worker subagent pattern for probe-heavy batches only when parallel help is explicitly requested. Treat it as operator guidance, not harness state; retained eval decisions stay with the main coordinator.
- Stop spending whole rounds on scalar classifier terms that only add or damp one hazard value; recent signed-impact and reversion-veto probes were either exact no-ops or over-open regressions.
- Treat support-only positives as stabilizers, not primary search ideas. `CappedLeakageRebateSuppression`, `ConsumedWidthRefillAmplificationVeto`, and `PassiveRecaptureDecomposition` should not be stacked together without a larger primary anchor.
- Do not recombine weak anchors across multiple downstream layers. Combination candidates should have one primary interface owner and at most one bounded secondary adjunct.
- Do not treat age-ledger or premium-cap language as sufficient novelty. Round 28 showed that aged evidence caps can still act like hidden release paths even when implemented outside the first risk-signal insertion point.
- Do not treat public market-design or batch-auction language as sufficient novelty by itself. Round 29 showed temporal clearing clocks can still become broad protection classifiers unless the contract prevents fee overcharge before hazard/shared-spread consumption.
- Require at least one candidate outside incumbent vocabulary before the next source batch if every draft uses only OOB, route/gap hazard, flow ownership, inventory overlay, burst admission, recenter release, quiet-state refill, or scalar hazard damping.
- Favor interface-contract changes over coefficient changes:
  - separate adverse-selection protection evidence from benign-flow fee-capture evidence
  - keep upstream interpretation changes upstream of shared spread and side-specific protection
  - state allowed consumers and forbidden consumers before writing Solidity
  - prove layer ownership in the plan before source work
- Round 18 scratch lesson: public microstructure-inspired toxicity timing was structurally distinct but hurt low-decile in its first activation; a future retry needs a floor-preserving estimator selector, not stronger toxicity coefficients.
- Round 21 scratch lesson: downstream final-quote arbitration and safe-side service admission both collapsed floors; Round 22 should avoid layer 6 and avoid final-quote-only arbiters.
- Round 22 scratch lesson: upstream confidence/reconstructability/quorum classifiers collapsed even harder. Use external AMM/microstructure guidance before another batch and avoid trust-gate designs that attenuate protection.
