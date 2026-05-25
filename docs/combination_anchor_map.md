# combination_anchor_map

Seeded from `apr21-screen490-1431`.
This is the persistent cross-round synthesis surface for combination planning.
Append only durable positive anchors, compatibility/collision notes, and saturated failure modes that remain useful after a single round closes.

## 00 Agent Query Index

Use this file as a decision map, not as a narrative log. It should answer four agent questions quickly:

1. What is the active seed/comparison frame?
2. Which anchors are still useful, and under what compatibility constraints?
3. Which failure basin is this new idea likely to replay?
4. What must a proposer, critic, or worker decide before source edits?

Read order for a probe-heavy round:

| Need | Read first | Then read |
| --- | --- | --- |
| Current seed and parked anchors | [Retained Context](#01-retained-context) | [Anchor Decision Router](#02-anchor-decision-router) |
| Proposing a candidate | [Immediate Combination Rules](#06-immediate-combination-rules) | [Proposal Admission](#proposal-admission) |
| Critic narrowing | [Failure Basin Query Table](#05-failure-basin-query-table) | [Critic Gates](#critic-gates) |
| Diagnosing low hit rate | [Meta Search Lessons](#meta-search-lessons) | [Proposal Admission Scorecard](#proposal-admission-scorecard) |
| Worker handoff | [Worker Handoff](#worker-handoff) | [Round Lessons To Carry Forward](#round-lessons-to-carry-forward) |
| Adding durable evidence | [Entry Format](#08-entry-format) | The relevant anchor or basin detail section |

Stable search tokens:

- `seed-frame`: active lane, incumbent, parked comparison anchors.
- `positive-anchor`: reusable signal with compatibility and collision notes.
- `support-only`: stabilizer that cannot be a primary thesis.
- `failure-basin`: repeated profile signature that should reject similar proposals early.
- `admission-gate`: proposer requirements before source work.
- `critic-gate`: rejection checks before worker handoff.
- `worker-stop`: scratch result classification and bounded follow-up rules.
- `round-lesson`: durable but chronology-shaped evidence from prior rounds.
- `proposal-scorecard`: structured fields required before source work.
- `consumer-contract`: allowed and forbidden downstream readers for new evidence.
- `search-frame-change`: explicit seed, ban-list, or external-mechanism pivot after saturation.

## 01 Retained Context

- Historical Apr21 official incumbent remains `screen_0001` at `485.92377070367183` mean edge; active May09 incumbent state is listed below.
- Active May09 floor-seed lane is `may09-screen490-floor-0001`, seeded as `screen_0001` / `RegimeSelectorStrongerFloor` at `487.01236396243195`; its current best raw is `screen_0006` / `Event140Recapture` at `491.910339497031`, status `discard`. The recently retired QTRS lane best raw was `screen_0004` / `MajorizationRiskVectorFilter` at `487.7232131981818`, status `discard`.
- Parked cross-run best raw retained discard is May08/Apr21 `screen_0008` / `WeakConsistencyEventFeasibilityMask` at `488.03274719863765` mean edge.
- Use this note for scratch-round combination planning only; it does not change retained promotion semantics.
- External phenotype calibration from the Apr 23 authorized oracle probe: the target space has much lower arb leakage/selectivity, lower mean fee, and materially higher floor slices than current local anchors.
- Treat oracle information only as phenotype evidence. Do not inspect or copy oracle/reference implementation details unless the active task explicitly authorizes it.

## 02 Anchor Decision Router

| Tag | Anchor or family | Agent decision |
| --- | --- | --- |
| `seed-frame` | Active May09 `RegimeSelectorStrongerFloor` seed | Use as the current floor-preserving frame, not as permission for selector-polish rounds. |
| `active-best-raw` | May09 `Event140Recapture` | Continue only from canonical `screen_0006`; it clears the Round 13 screen threshold through lower event carry plus stronger passive recapture, but has not been holdout-confirmed. |
| `parked-best-raw` | May08/Apr21 `WeakConsistencyEventFeasibilityMask` | Keep as parked comparison evidence for one-way event-feasibility validation; do not tune residual weights locally. |
| `parked-qtrs` | Retired `MajorizationRiskVectorFilter` | Treat as a weak measurement anchor from the retired QTRS lane; do not reopen vector-order filter polish without a new owner. |
| `floor-first-near-miss` | Scratch `RetailFloorFirstStatePartition` | Reuse only with a different primary interface or fee-band-preserving boundary. |
| `support-only` | `ConsumedWidthRefillAmplificationVeto`, `PassiveRecaptureDecomposition`, `CappedLeakageRebateSuppression` | May stabilize another thesis; must not become the primary search idea. |
| `layer-5-6-diagnostic` | Inventory/toxic-side and final-quote adjacent work | Admit at most one diagnostic slot, only with out-of-distribution vocabulary and a hard no-release boundary. |

Default stance: one primary anchor, at most one secondary adjunct, and no retained-eval consideration unless the scratch result beats live `best_raw` or creates a genuinely new floor-risk owner with materially better named floor slices.
Current low-hit-rate diagnosis: recent accepted proposals usually failed because the proposal changed source vocabulary but not the consumer path, or because a mechanical boundary preserved one contract by starving benign cuts/recentering. The recurring failure is new evidence flowing into existing hazard, protection, release, side-risk, service, tail-consumer, cut, or recenter logic without a boundary that preserves benign floors.

## 03 Positive Anchors By Scaffold Layer Or Family

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

### Layer 1-3 observation basis, tail state, and classifier evidence

- `screen_0008` / `WeakConsistencyEventFeasibilityMask`
  - Signal: `+2.108976494965816` mean edge vs incumbent and `+0.4893356356802201` vs prior best raw `screen_0007`; improved `arb_loss_to_retail_gain=0.08680487844146438`, `quote_selectivity_ratio=17.3749619948117`, `low_decile_mean_edge=372.41891117598567`, `low_retail_mean_edge=417.8656683116062`, and `low_volatility_mean_edge=465.1871007698987` while keeping `time_weighted_mean_fee=0.004995975154787965` below the Round 39 overcharge kill band.
  - Compatibility: parked cross-run best raw anchor for weak LOB event-feasibility validation. It is useful as a one-way uncertainty/feasibility residual that can raise protection evidence when observed trade direction contradicts price-path movement without authorizing release, refill, recapture, opportunity, final-quote edits, or tail-consumer behavior.
  - Collision: do not turn the next round into feasibility-residual coefficient tuning. The productive signal was the mechanical event-path validity owner; local scalar residual weight polish risks replaying firewall / classifier-local floor-drag plateaus.

- `screen_0007` / `QuantileTailRiskSketch`
  - Signal: `+1.619640859285596` mean edge vs incumbent and `+0.38094996876094456` vs prior best raw `screen_0006`; improved `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge` versus `screen_0006` while keeping `quote_selectivity_ratio=19.15842357425379` and `time_weighted_mean_fee=0.0048110022982122466` inside the Round 34 kill bands.
  - Compatibility: former best raw anchor for bounded distributional tail-state ownership. It is useful when a distinct primary topology needs discrete tail buckets that can feed classifier/firewall/protection floors without directly reshaping hazard/divergence or opening release paths.
  - Collision: do not turn Round 35 into tail-bucket coefficient polishing. The useful signal is the bounded tail-state interface; local scalar bucket thresholds risk replaying upstream codec/classifier plateau.

- `screen_0006` / `MonotoneEvidenceFirewallStrict`
  - Signal: `+1.2386908905246514` mean edge vs incumbent and `+0.15009763176453816` vs prior best raw `screen_0005`; improved `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `low_retail_mean_edge`, and `low_volatility_mean_edge` versus `screen_0005` while keeping `time_weighted_mean_fee` in the same band.
  - Compatibility: former best raw anchor and still useful for protection-preserving evidence boundaries. It is useful when a distinct primary topology needs a one-way boundary that can raise risk evidence but cannot authorize rebates, opportunity cuts, refill, recapture, inventory, final quote, or layer-4 release.
  - Collision: do not turn a future round into firewall coefficient polishing. The non-strict firewall was sub-best, and the positive result came from enforcing the one-way contract more clearly, not from making another scalar hazard damper.

- `screen_0005` / `RegimeSelectorStrongerFloor`
  - Signal: `+1.0885932587601133` mean edge vs incumbent; improved `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge` versus the incumbent and improved all tracked floor slices versus `screen_0004`.
  - Compatibility: former best raw anchor and still useful as a floor-preserving upstream/mid-scaffold selector when paired with a structurally different primary topology.
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

## 04 Support-Only Controls

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

## 05 Failure Basin Query Table

Use this table before reading the detailed basin entries. If a proposal matches the symptom and source vocabulary, reject it unless it names a mechanical boundary that prevents the listed failure.

| Fast grep token | Likely basin | Reject or require |
| --- | --- | --- |
| `release`, `relief`, `discount`, `opportunity`, `calm` | Hidden-release / over-open basins | Hard no-release proof before any consumer can lower protection. |
| `fee`, `rent`, `surcharge`, `overcharge`, `worst-slice` | Over-tightening / overcharge basins | Benign-capture and floor preservation proof before shared spread changes. |
| `codec`, `geometry`, `divergence`, `path`, `residual` | Upstream geometry-codec plateau | Named downstream owner that changes protection-vs-benign allocation. |
| `classifier`, `certificate`, `quorum`, `trust`, `abstention` | Classifier-local floor-drag or estimator over-open | One-way boundary and kill signature versus live `best_raw`. |
| `allocation`, `account`, `escrow`, `symmetry`, `surplus` | Layer-4 allocation-release basin | Hard floor-preservation invariant before width-release authority. |
| `tail`, `pickoff`, `stop`, `bucket` | Tail-consumer over-open collapse | Proof that tail evidence cannot widen release or starve floors. |
| `queue`, `depth`, `latency`, `fill`, `resilient` | Queue/depth open-release collapse | Read-only diagnostic or hard no-release proof before any consumer sees it. |
| `causal`, `directional`, `mass`, `convexity`, `rank`, `continuity` | Label hidden-release basins | Independent floor invariant; labels alone are not novelty. |
| `service`, `capacity`, `slope`, `isoquant`, `elasticity` | Service-capacity no-op / floor-loss frame | Different seed or non-service primary owner before more source work. |
| `process-control`, `Lyapunov`, `barrier`, `CUSUM`, `insurance` | Current floor-seed add-only control failures | New downstream consumer contract, not another label into existing hazard/side-risk consumers. |
| `cut`, `budget`, `meter`, `drawdown`, `recenter` | Cut-boundary starvation / floor-drag failures | New seed/search frame or proof that the boundary preserves safe-side cuts and recentering before more source work. |
| `capability`, `predicate`, `antichain`, `wavelet`, `Tukey`, `morphology`, `count-min`, `e-process` | OOD additive-hold floor-collapse failures | New search frame or non-additive primary owner; do not soften add-only holds on `OracleTradeToxCoef6500`. |

## Saturated Failure Modes

Keep this section extensible. Add a new failure mode when repeated probes share a profile signature that is not well described by the current vocabulary; prefer a precise phenotype name over forcing evidence into `over_open_leak`, `over_tighten_clamp`, `frontier_neighbor`, or `crossover_regression`. A useful entry names the signature, repeated sources, and the critique question that should block similar future ideas before source work.

- Over-open leak basin
  - Signature: `quote_selectivity_ratio` drifts into roughly the high `20s` through `70+`, mean fee softens, arb leakage rises, and low-decile quality collapses.
  - Repeated sources: `ConfidenceDebtEstimator`, `ShockCarryInsuranceBudget`, `InventorySkewCenteringOverlay`, `RetailFloorGuardedInventoryOverlay`, `BasisOwnedClassifierExports`, `DualAnchorQuoteTopology`, `ProfileTargetShadowNormalizer`, `PriorTradeMarkoutLedger`.

- Over-tightening basin
  - Signature: mean fee spikes or selectivity collapses too far, benign capture disappears, and most slices degrade together.
  - Repeated sources: `CarrySplitAssembler`, `BoundaryNormalizedStateLoop`, `AdverseExtensionFloorGuard`, `ElapsedGapHazardClassifier`; `ImpactSplitHazard` also leaned into this direction even though its arb metrics improved.

- Phenotype-identical no-op plateau
  - Signature: source edits look new, but screen phenotype stays identical or effectively unchanged.
  - Repeated sources: `PersistenceShapedObservationBasis`, `PersistenceWeightedParticipationHazard`, `RecenterReleaseConfirmation`, `RatchetConfidenceVeto`, `PathReversalResidueTransform`.
  - Use: block proposals whose expected movement is only "stay near the incumbent." Require a named metric to move by enough to distinguish the probe from incumbent noise before worker source edits.

- Weak-anchor clone saturation
  - Signature: a tiny anchor gets recopied locally until attribution gets worse and the batch collapses around one weak motif.
  - Repeated sources: inventory-overlay quiet-state tapers, typed-export ownership changes that touch recapture eligibility, direct latent/quote crossovers, standalone burst-label relaxations, and OOB-dependent short-gap or inventory recombinations.
  - Use: reject batches that combine several sub-`0.1` positives or local variants of one anchor. One weak support signal may accompany a stronger primary owner; it should not define the batch.

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

- Upstream geometry-codec plateau
  - Signature: a layer 1/2 observation or latent-state geometry codec avoids catastrophic leakage and stays near the incumbent fee/selectivity band, but remains below `screen_0005` and does not create a new floor-risk owner.
  - Repeated sources: `PathReversalResidueTransform`, `FairValueCorridorProjector`, `MarginalSlopeDisplacementCodec`, `BandpassDivergenceEncoder`.
  - Use: do not spend another full round on hazard/divergence input reshaping, fair-value projector geometry, or curve-shape residual codecs unless a different primary anchor owns protection-vs-benign-capture allocation. `BandpassDivergenceEncoder` can remain a diagnostic adjunct because it improved floor slices versus incumbent, but it should not receive local coefficient polish.

- Broad-protection starvation basin
  - Signature: a protection-only classifier or geometry signal avoids over-open leakage but pushes fees/protection high enough that mean edge and all floor slices collapse.
  - Repeated sources: `BatchClearingLatencyPressure`, `ReserveBandExhaustionClassifier`, `VolumeBucketImbalanceLattice`, `RetailCaptureInvariantProjector`, `LossBudgetedSideProtectionIntegrator`.
  - Use: do not retry broad latency-pressure or reserve-exhaustion classifiers unless the interface includes an explicit cap that preserves retail capture and keeps the incumbent fee band interpretable.

- Temporal-clearing overprotection basin
  - Signature: a discrete-time, latency, collision, or batch-pressure interface looks structurally distinct, but the classification feeds hazard/shared protection too broadly: fees rise above the incumbent band, selectivity climbs, and all tracked floor slices break.
  - Repeated sources: `BatchClearingLatencyPressure`, `BatchCollisionObservationSplitter`, `DiscreteClearingClockState`.
  - Use: do not retry temporal clearing or batch-pressure classifiers as a primary scoring idea unless the interface has a hard no-overcharge boundary and can preserve benign retail capture before touching hazard or shared spread.

- Aged-premium release basin
  - Signature: a layer 2 evidence lifetime or layer 4 premium cap appears to target high-fee floor protection, but instead releases too much downstream behavior: `quote_selectivity_ratio` around `70`, `time_weighted_mean_fee` around `0.00361`, and low-decile / low-retail floors collapse.
  - Repeated sources: `AgingEvidenceLedgerWithPremiumBudgetCap`, `AgingEvidencePostCutPremium`.
  - Use: do not retry the Round 27 high-fee fix by adding another cap to floor-risk or evidence-age terms. Future fee-band preservation needs an interface that cannot feed opportunity cuts, inventory, final quote selection, or shared fee compression.

- Layer-4 allocation-release basin
  - Signature: an allocation-owner or account-separation interface sounds like it preserves protection-vs-benign-capture attribution, but the implementation gives layer 4 too much width-release authority: `quote_selectivity_ratio` jumps into roughly `28-73`, `time_weighted_mean_fee` falls toward `0.00355-0.00450`, and low-decile / low-retail / low-volatility floors break.
  - Repeated sources: `RetailSurplusConservationAccount`, `ToxicityCostInventorySeparation`, `CrossSideSymmetryDebt`, `TwoAccountSpreadAssembly`.
  - Use: reject standalone layer 4 allocation ledgers unless they contain a hard mechanical floor-preservation invariant before any fee release path. Do not treat account/escrow/surplus/symmetry vocabulary as novelty unless the consumer boundary prevents broad shared-spread compression.

- Classifier-local floor-drag plateau
  - Signature: classifier-local evidence keeps the profile near the incumbent but moves floor slices slightly negative and fails to create a new anchor.
  - Repeated sources: `ClassifierExportSplit`, `TypedClassifierExportFirewall`, `RouteQualityCalmHazardPartition`, `ConformalAbstentionCertificate`, `IndependentEvidenceQuorumRouter`, `MinimumRetailServiceCertificate`, `ResidualRetailConvexityPartition`, `AdverseSelectionAbstentionBus`.
  - Use: allow at most one softened follow-up when the interface remains classifier-local and does not feed global calm or recapture eligibility.

- Tail-consumer over-open collapse
  - Signature: a tail-state or pickoff-state consumer appears bounded upstream, but downstream consumption turns it into broad release or leakage: `quote_selectivity_ratio` rises into roughly `42-59`, `arb_loss_to_retail_gain` rises above `0.20`, and low-decile falls toward `213-226`.
  - Repeated sources: `TailBucketConsumerTransducer`, `PickoffExposureStopLoss`, `SequentialAdverseStopTest`.
  - Use: do not locally rewrite `screen_0007` tail-bucket consumers, stale-pickoff exposure states, or bounded stop-state consumers unless the proposal proves a mechanical boundary that cannot widen release or starve floors after evidence enters the pipeline.

- Mix-state over-open collapse
  - Signature: a counterparty, participation, or mix-stability state looks upstream and bounded, but downstream consumption lowers fees or weakens protection enough that selectivity jumps above roughly `50` and all floor slices break.
  - Repeated sources: `CounterpartyMixStabilitySketch`.
  - Use: do not retry mix-stability sketches as primary topology until the state is provably read-only diagnostic or has a hard no-release proof before any classifier or protection consumer sees it.

- OOD additive-hold floor-collapse basin
  - Signature: non-Reference OOD mechanisms are kept out of release/opportunity paths and used only as additive post-assembly holds, but the route-level phenotype still collapses: low-decile falls to roughly `222.8589` or `205.0163`, selectivity rises into roughly `23-88`, and fee behavior either softens below `0.0049` or overcharges without floor repair.
  - Repeated sources: `PredicateTransformerFloorInvariant`, `CapabilityStampedProtectionFloor`, `AntichainContradictionHold`, `WaveletImpulseHoldBus`, `TukeyBiweightOutlierHold`, `MorphologicalCloseOpenFloorGuard`, `CountMinHeavyHitterToxicFlowHold`, `EProcessSequentialHold`.
  - Use: do not continue capability stamps, predicate-transformer invariants, antichain contradiction holds, wavelet/morphology/robust/sketch/sequential-evidence holds, or smaller add-only variants on `OracleTradeToxCoef6500`. The next branch needs a new search frame or a non-additive primary owner before quote-path hold logic.

- Attribution-state over-open collapse
  - Signature: a continuation, symmetry, or invariant-loss attribution state sounds like a new upstream owner, but downstream consumption behaves like hidden fee relief: `quote_selectivity_ratio` rises to roughly `70`, `time_weighted_mean_fee` falls to roughly `0.00361-0.00363`, and low-decile / low-retail floors collapse.
  - Repeated sources: `MatchedImpactContinuationState`, `InvariantLossAttributionSplitter`, `HawkesExcitationSourceSplitter`.
  - Use: do not retry continuation or invariant-loss attribution as a primary topology unless the state is mechanically read-only or can only add a hard spread hold with no path into calm, release, opportunity, inventory, final quote, or fee compression.

- Worst-slice assembly overcharge basin
  - Signature: a layer-4 worst-case or min-slice spread assembler appears floor-preserving, but aggregate protection overcharges, selectivity breaks, and all tracked floor slices collapse.
  - Repeated sources: `WorstSliceSpreadAssembler`.
  - Use: reject worst-slice shared-spread aggregation unless a separate benign-capture conservation proof caps overcharge before the layer-4 spread floor is applied.

- Source-deconvolution over-open collapse
  - Signature: an external microstructure source-splitting idea looks upstream and non-AMM, but deconvolution or excitation labels still weaken downstream protection: selectivity rises toward roughly `69-71`, `time_weighted_mean_fee` falls toward roughly `0.00361-0.00382`, and low-decile collapses near `213`.
  - Repeated sources: `BidAskBounceDeconvolutionBus`, `HawkesExcitationSourceSplitter`.
  - Use: do not treat bounce, excitation, or source-split vocabulary as sufficient novelty. Future source deconvolution must be read-only or must prove a hard no-release boundary before layer-3 / layer-4 consumers can act on it.

- Robust-demand leakage collapse
  - Signature: robust-statistics or demand-elasticity bins preserve or stabilize headline fee level but misallocate protection so badly that arb leakage rises above `0.30`, selectivity rises toward `69`, and low-retail / low-volatility floors collapse.
  - Repeated sources: `RobustRetailDemandElasticitySurface`.
  - Use: do not retry robust retail-demand bins as a primary topology until the contract proves the bins cannot lower protection for low-retail and low-volatility slices.

- Run-length / context-segment over-open collapse
  - Signature: BOCPD-style run-length or context-tree sequence segmentation looks upstream and public-evidence motivated, but downstream consumption behaves like hidden release: `quote_selectivity_ratio` rises toward roughly `67`, `time_weighted_mean_fee` falls toward roughly `0.00371-0.00372`, and low-decile collapses near `213.5`.
  - Repeated sources: `PosteriorRunLengthBoundaryTape`, `ContextTreeSymbolSegmentOwner`.
  - Use: do not retry run-length or context-tree segment labels as primary topology unless the segment state is read-only or can only add a hard no-release hold before any calm, release, hazard, or shared-spread consumer sees it.

- Liquidity-shortfall overcharge basin
  - Signature: liquidity-risk / placement-envelope language improves leakage and selectivity, but adds enough shared width that mean and all tracked floor slices fall below the best raw anchor while `time_weighted_mean_fee` rises above roughly `0.00520`.
  - Repeated sources: `LiquidityShortfallPlacementEnvelope`.
  - Use: do not retry liquidity-shortfall placement envelopes as direct shared-spread adders. Future liquidity-risk ideas need a floor-preserving owner that avoids both broad overcharge and layer-5 protection behavior.

- Queue/depth open-release collapse
  - Signature: queue, depth, passive-fill, latency-window, or depth-shape state looks like public microstructure evidence, but downstream consumption behaves like hidden relief: `quote_selectivity_ratio` rises toward roughly `51-80`, `arb_loss_to_retail_gain` rises above roughly `0.21`, mean falls far below `screen_0008`, and tracked floor slices break.
  - Repeated sources: `DepthImbalanceCrossingBarrier`, `PassiveQueueFillProbabilityWitness`, `LatencyAdverseWindowBudget`, `ResilientDepthShapeRecoveryState`.
  - Use: do not retry queue/depth witnesses as primary topology unless the state is read-only diagnostic or mechanically barred from release, fee compression, calm, opportunity, refill, recapture, final quote, or direct shared-spread control.

- Causal-label hidden-release collapse
  - Signature: a causal, directional-mass, or adverse-fill owner appears to preserve width only, but the label still reaches existing relief/protection consumers: `quote_selectivity_ratio` rises into roughly `55-60`, `arb_loss_to_retail_gain` rises above `0.22`, and low-decile collapses near `213.5`.
  - Repeated sources: `AdverseFillCausalityLedger`, `DirectionalAdverseMassSplitter`.
  - Use: do not retry causal or directional adverse-mass labels as primary topology unless the label is read-only diagnostic or has a hard no-release proof and cannot alter calm, opportunity, refill, recapture, final quote, inventory, shared-spread release, or side-specific relief.

- Generic uncertainty-label hidden-release collapse
  - Signature: a convexity, rank-stability, continuity, or other upstream uncertainty label appears one-way on paper, but downstream consumption still behaves like hidden release: `quote_selectivity_ratio` rises toward roughly `54-65`, `arb_loss_to_retail_gain` rises above roughly `0.23`, mean falls near `406-409`, and low-decile collapses near `213.5`.
  - Repeated sources: `ExecutionCostConvexitySurface`, `CrossScenarioRankStabilityOwner`, `RetailContinuityShockAbsorber`.
  - Use: stop adding new uncertainty labels into the existing consumer path unless the implementation proves the label cannot lower protection, cannot influence calm/release/refill/recapture/opportunity/final quote, and has an independent floor-preservation invariant.

- Relief-removal overcharge / floor-loss basin
  - Signature: controlled deletion or nullification of relief/discount consumers improves leakage and selectivity, but raises effective fee / protection enough to lose mean and all tracked floor slices versus `screen_0008`.
  - Repeated sources: `FeasibilityReliefConsumerPruner`, `UnsafeDiscountBranchNullifier`.
  - Use: do not retry simple removal of discount or relief branches as a primary topology. Future downstream work must preserve benign floor slices before disabling relief, not just lower leakage.

- Mechanical isolation hidden-release basin
  - Signature: private-lane isolation or local width monotonicity sounds mechanically safe, but downstream interactions still reopen leakage: selectivity rises above roughly `32-47`, low-decile and low-retail floors fall sharply, and mean stays far below `screen_0008`.
  - Repeated sources: `OneWayWidthMonotonicityAssembler`, `ProtectedPathConsumerIsolation`.
  - Use: do not spend another worker on mechanical lower envelopes or private lanes unless the design also proves benign floor preservation and avoids the existing downstream interaction path entirely.

- Cut-boundary starvation / floor-drag basin
  - Signature: a cut-budget, cut-meter, drawdown seal, or recenter-permission boundary sounds mechanically safe because it blocks relief or state relaxation, but measurement shows either severe safe-side cut starvation with `quote_selectivity_ratio` rising into roughly `43-67`, low-decile falling toward `213-247`, and low-volatility near `410-416`, or a near-frontier floor drag that improves leakage/selectivity only by tiny amounts while losing mean and all tracked floor slices.
  - Repeated sources: `CutSolvencyFloorBudget`, `LeakyCutAdmissionMeter`, `FloorBufferBeforeRecenter`, `LVRReadOnlyDrawdownSeal`.
  - Use: do not continue cut-solvency budgets, leaky cut meters, aggregate cut caps, drawdown cut seals, or pre-recenter floor buffers under the active floor seed unless the next proposal changes seed/search frame or proves a consumer that neither starves safe-side cuts nor routes into hidden release.

## 06 Immediate Combination Rules

- Draft around one primary anchor and at most one secondary adjunct.
- Keep `OrthogonalObservationBasis` optional, not mandatory infrastructure for every probe.
- Treat `InformationLiquiditySplitBusHardGuard` as the leading upstream anchor; follow-ups must explain how they preserve its leakage/selectivity improvement instead of merely increasing hazard or fees.
- Treat active-run `screen_0001` / `RegimeSelectorStrongerFloor` as a floor-seed frame, not a selector-polish target. Keep the retired QTRS `screen_0004` / `MajorizationRiskVectorFilter` and May08/Apr21 `screen_0008` / `WeakConsistencyEventFeasibilityMask` as parked comparison anchors, but require the next batch to add a different primary topology instead of locally polishing selector thresholds, fee-band coefficients, event-feasibility residual weights, flow-share entropy, acceleration pulse coefficients, or bid/ask vector-order filters. Keep `screen_0007` as the prior bounded tail-state reference, `screen_0006` as the prior one-way firewall reference, and `screen_0005` as the active floor-preserving selector seed reference.
- If `burst-pivot` is reused, pair it only with a floor-preserving partner and keep the burst admission narrow.
- Layer 5/6 is not categorically banned, but it is no longer an in-distribution exploit-polish surface. Admit at most one layer-5/6 diagnostic slot when it comes from an out-of-distribution mechanism vocabulary, names a new evidence owner, and proves a hard boundary against broad release, refill, recapture, opportunity, inventory-overlay replay, final quote, and fee compression.
- Pause OOB plus inventory and OOB plus short-gap combinations until a new non-OOB upstream anchor exists.
- Reject any draft that broadens safe-side opportunity, lowers fees across the board, or stacks several small safe signals with weak attribution.
- Reject any draft whose only novelty is outside vocabulary. `physical reservoir`, `danger`, `Lyapunov`, `barrier`, `service`, `causal`, `queue`, or similar labels do not count unless the proposal changes which consumer owns the resulting signal.
- When the current ban set leaves no four-design batch, do not pad the round with weak variants. Record a `search-frame-change`: switch seed/anchor frame, deliberately relax one banned family with tight kill thresholds, or import a new external mechanism class with a new consumer contract.

## 07 Productivity Rules For Future Rounds

### Meta Search Lessons

- The hit-rate bottleneck is admission quality, not scratch execution. Workers have repeatedly implemented critic-accepted contracts correctly, but the accepted contracts often allowed hidden release, overcharge, or floor starvation once measured.
- OOD vocabulary is useful only as a candidate generator. It is not evidence of novelty after many failures from process control, runtime assurance, danger theory, physical reservoirs, queue/depth, service capacity, causal labels, robust demand, and market-design terms.
- Seed changes can unlock a few weak lifts, but local repair around the new seed saturates quickly. May09 QTRS advanced best raw in tiny steps while giving back floor slices; the floor-seed lane then rejected add-only controls and upstream OOD labels outright.
- Positive anchors should be treated as interface evidence, not coefficient surfaces. `WeakConsistencyEventFeasibilityMask`, `QuantileTailRiskSketch`, `MonotoneEvidenceFirewallStrict`, and `RegimeSelectorStrongerFloor` are useful because of their owner contracts, not because their local scalar thresholds deserve polishing.
- The strongest early reject signal is a missing `consumer-contract`. If the proposal cannot name allowed readers, forbidden readers, and a mechanical proof that forbidden readers cannot indirectly act, it is likely to replay a hidden-release or overcharge basin.
- The second strongest early reject signal is an unpriced floor tradeoff. Proposals that improve leakage/selectivity while raising fees or lowering low-decile / low-retail slices need a floor-repair owner before they deserve another worker.
- Saturation gates are productive. Rounds 44, 48, May08 Round 3, and May09 QTRS Round 5 were better outcomes than padded batches because they forced a seed or search-frame decision instead of adding more weak names.
- Under the active floor-seed lane, mechanical boundaries are now failing in both directions: upstream labels become hidden release, while cut/recenter boundaries starve benign paths or create near-frontier floor drag. The next productive proposal should change the seed/search frame or import a mechanism class that is neither upstream observation shaping nor cut/recenter gating.
- May13 oracle ablations are distilled in `docs/reference_oracle_evidence_cards.md`. Durable rule: `Reference.sol` wins through integrated fair-mid / toxicity / side-protection / congestion-fee ownership, while direct fair-mid, lambda, low-base, or side-shift transplants into fixed frontier consumers are strongly negative. One robust direct transplant survived confirm: `WeakConsistencyEventFeasibilityMask + ref_trade_tox_boost` at `+1.305` paired delta over 512 seeds. Current frontier event carry and quiet recenter are load-bearing; shared calm rebate and refill auction are near-neutral diagnostics. Future use of oracle-shaped evidence must redesign allowed consumers before publishing it into hazard, protection, opportunity, or shared-spread paths.

### Proposal Admission

- Use the optional proposer / critic / worker subagent pattern for probe-heavy batches only when parallel help is explicitly requested. Treat it as operator guidance, not harness state; retained eval decisions stay with the main coordinator.
- In subagent-assisted probe rounds, critic narrowing must not leave fewer than four accepted strategy design improvements. Iterate proposer -> critic -> proposer until at least four distinct topology/layer/vocabulary/design/nonlinearity candidates have positive expected movement in mean edge or a named problem-space metric.
- Each proposed design must state one primary interface owner, allowed consumers, forbidden consumers, expected metric movement, and a kill signature tied to the active run's live `best_raw` plus any explicitly named parked comparison anchor. Reject drafts that describe only a variable, coefficient, or renamed incumbent signal.
- Require at least one candidate outside incumbent vocabulary before source work if every draft uses only OOB, route/gap hazard, flow ownership, inventory overlay, burst admission, recenter release, quiet-state refill, or scalar hazard damping.
- Treat public market-design, AMM, and microstructure language as source material, not novelty proof. Prefer deliberately out-of-distribution search vocabulary over more in-distribution AMM/LOB/hazard/refill/recapture/opportunity terms when the current lane is saturated; the proposal still needs a new evidence owner and a protection-preserving boundary.
- A layer-5/6 proposal is admissible only as a bounded diagnostic when its source vocabulary is out-of-distribution and the interface contract prevents incumbent-local exploit polish. Reject layer-5/6 drafts that merely rename safe-side service, refill, recapture, inventory centering, opportunity, or final-quote behavior.

### Proposal Admission Scorecard

Use this before worker handoff. A candidate with any blank or narrative-only answer should be rejected or sent back to proposer.

| Field | Accept | Reject |
| --- | --- | --- |
| `primary_owner` | Names one scaffold interface and its state transition. | Names a family, label, or coefficient without ownership. |
| `consumer_contract` | Lists allowed readers and exact allowed actions. | Lets existing hazard/protection/release consumers infer behavior implicitly. |
| `forbidden_consumers` | Mechanically bars release, refill, recapture, opportunity, calm, final quote, direct fee/base spread, inventory overlay, and hidden relief unless one is the explicit owner. | Says "bounded" or "one-way" without proving who cannot read it. |
| `nearest_negative_example` | Names the closest basin and the profile movement that would distinguish this probe. | Claims novelty because the source vocabulary is new. |
| `metric_budget` | States expected movement and max tolerated damage for `mean_edge`, `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge`. | Optimizes one metric while hand-waving floor slices. |
| `kill_signature` | Stops on no-op, hidden release, overcharge, or floor-starvation profiles before coefficient polish. | Allows follow-up tweaks after the first result lands in a known basin. |

### Critic Gates

- Stop spending whole rounds on scalar classifier terms that only add or damp one hazard value; recent signed-impact and reversion-veto probes were either exact no-ops or over-open regressions.
- Treat support-only positives as stabilizers, not primary search ideas. `CappedLeakageRebateSuppression`, `ConsumedWidthRefillAmplificationVeto`, and `PassiveRecaptureDecomposition` should not be stacked together without a larger primary anchor.
- Do not recombine weak anchors across multiple downstream layers. Combination candidates should have one primary interface owner and at most one bounded secondary adjunct.
- Do not treat age-ledger or premium-cap language as sufficient novelty. Round 28 showed that aged evidence caps can still act like hidden release paths even when implemented outside the first risk-signal insertion point.
- Do not treat public market-design or batch-auction language as sufficient novelty by itself. Round 29 showed temporal clearing clocks can still become broad protection classifiers unless the contract prevents fee overcharge before hazard/shared-spread consumption.
- Reject another layer 1/2 geometry-codec batch unless it can name the downstream owner that changes protection-vs-benign-capture allocation. Round 30 and Round 31 showed that safe upstream codecs can remain near-frontier without becoming productive anchors.
- Favor interface-contract changes over coefficient changes:
  - separate adverse-selection protection evidence from benign-flow fee-capture evidence
  - keep upstream interpretation changes upstream of shared spread and side-specific protection
  - state allowed consumers and forbidden consumers before writing Solidity
  - prove layer ownership in the plan before source work
- Reject OOD proposals that fail the same `consumer-contract` check as in-distribution proposals. A new metaphor cannot rescue an old consumer path.
- If the critic rejects most of a batch for the same reason, update the active run note and this map before requesting another proposer pass. Do not let the next prompt rediscover the same negative examples from scratch.

### Worker Handoff

- Workers should receive only critic-accepted contracts with a single scratch path, validation command, probe command, and stop rule. They should not open new topology families mid-worker-loop.
- The first scratch result should be classified against the precise failure-mode vocabulary above before any bounded tweak. If the result lands in `Phenotype-identical no-op plateau`, `Upstream geometry-codec plateau`, `Over-open leak basin`, or `Broad-protection starvation basin`, stop rather than coefficient-polish.
- A scratch candidate should receive retained-eval consideration only if it beats the active run's live `best_raw` or misses it with a genuinely new floor-risk owner and materially better named floor slices. Near-incumbent safety alone is not enough.

### Round Lessons To Carry Forward

- Round 18 scratch lesson: public microstructure-inspired toxicity timing was structurally distinct but hurt low-decile in its first activation; a future retry needs a floor-preserving estimator selector, not stronger toxicity coefficients.
- Round 21 scratch lesson: downstream final-quote arbitration and safe-side service admission both collapsed floors; Round 22 should avoid layer 6 and avoid final-quote-only arbiters.
- Round 22 scratch lesson: upstream confidence/reconstructability/quorum classifiers collapsed even harder. Use external AMM/microstructure guidance before another batch and avoid trust-gate designs that attenuate protection.
- Round 27 scratch lesson: `RetailFloorFirstStatePartition` is a strong positive scratch anchor but carries a high-fee phenotype and missed `screen_0005`; future reuse needs a distinct primary topology or fee-band-preserving boundary, not local floor-partition polish.
- Round 28 scratch lesson: aged-evidence premium caps and post-cut premium placement both replayed the same low-fee over-open release; do not treat insertion-point movement as a new topology when the phenotype is unchanged.
- Round 29 scratch lesson: temporal clearing and batch-pressure ownership can invert into high-fee overprotection; require a hard no-overcharge cap before any new temporal/latency/collision design reaches hazard or shared spread.
- Round 30 scratch lesson: bounded path-reversal residue respected the layer 1 -> layer 2 boundary but was near-no-op and slightly sub-incumbent. Do not rerun small observation-input damping passes unless the next proposal owns a genuinely different primary topology and precommits to movement away from the incumbent phenotype.
- Round 31 scratch lesson: public microstructure / AMM evidence did not prevent entropy collapse by itself. Prior-fill markout replayed over-open release when routed into the same upstream hazard/divergence consumers, while fair-value corridor, marginal-slope residual, and bandpass divergence stayed below `screen_0005`; future external-evidence imports need a new protection-preserving owner, not another observation codec.
- Round 32 scratch lesson: allocation-owner and account-separation vocabulary did not prevent over-open release. Retail surplus, toxicity/inventory separation, cross-side symmetry debt, and two-account spread assembly all failed once layer 4 could release too much width; future allocation work needs a hard floor-preservation invariant before shared-spread compression.
- Round 33 scratch lesson: one-way risk evidence boundaries are live, but only when strict enough to preserve the floor without opening release paths. `MonotoneEvidenceFirewallStrict` advanced best raw to `screen_0006`; debt-before-repair and counterfactual regret memories replayed over-open release and should not be followed locally.
- Round 34 scratch lesson: bounded distributional tail buckets are live, but the positive result is tail-state ownership, not another upstream scalar codec. `QuantileTailRiskSketch` advanced best raw to `screen_0007`; public-shock and benign-exclusion variants were tiny near-frontier moves, while hysteretic latch, rank-copula, and meet-semilattice quote compilation either over-tightened, damaged floors, or collapsed selectivity.
- Round 35 scratch lesson: diversified interfaces across layers 1-4 did not advance retained state. `CurvatureExposurePassport` improved leakage/selectivity but lost mean and all tracked floors, so keep it as a bounded diagnostic adjunct only. Tail-bucket consumers, pickoff exposure accounting, and SPRT-style stop states collapsed into a new tail-consumer over-open basin, while the layer-4 no-release projector over-tightened and damaged benign capture.
- Round 36 scratch lesson: operating-boundary and mix-stability interfaces did not advance retained state. `RetailThroughputPreservationCap` was a baseline replay, `IndependentEvidenceQuorumRouter` and `MinimumRetailServiceCertificate` were classifier/certificate floor-drag variants, `CounterpartyMixStabilitySketch` opened a new mix-state over-open collapse, and the single layer-5 `LossBudgetedSideProtectionIntegrator` over-tightened. Future rounds need a different primary floor-risk owner rather than another guard/certificate/cap around existing consumers.
- Round 37 scratch lesson: floor-risk ownership words did not guarantee new behavior. `ResidualRetailConvexityPartition` and `AdverseSelectionAbstentionBus` were classifier-local floor-drag variants, `MatchedImpactContinuationState` and `InvariantLossAttributionSplitter` became attribution-state over-open collapses, and `WorstSliceSpreadAssembler` overcharged into floor destruction. Future rounds should demand mechanical isolation from relief/overcharge paths, not just new upstream vocabulary.
- Round 38 scratch lesson: diverse external-topology imports did not advance retained state. `BidAskBounceDeconvolutionBus` and `HawkesExcitationSourceSplitter` collapsed into over-open release, `RobustRetailDemandElasticitySurface` created a robust-demand leakage / floor-collapse phenotype, and `CrossImpactResidualOwnershipSplitter` was incumbent-equivalent. Future literature-inspired probes need mechanical no-release or no-floor-damage proofs, not only non-AMM terminology.
- Round 39 scratch lesson: weak LOB event-feasibility validation is live and advanced best raw to `screen_0008`; the productive part is a one-way event-path validity residual, not another scalar firewall pass. BOCPD run-length and context-tree segment labels replayed over-open hidden-release profiles, liquidity-shortfall placement overcharged into floor loss, and median-of-means floor-loss aggregation was near-frontier but sub-`screen_0007`, so future rounds should not locally tune those support controls.
- Round 40 scratch lesson: queue/depth microstructure imports did not advance retained state. Depth imbalance, passive fill probability, latency adverse windows, and depth-shape recovery all collapsed into open-release or adverse-leakage profiles, so future queue/depth work needs a read-only diagnostic or hard no-release proof before any consumer sees it.
- Round 41 scratch lesson: causal ownership and conservation vocabulary did not prevent hidden release. `AdverseFillCausalityLedger` and `DirectionalAdverseMassSplitter` collapsed into high-selectivity causal-label release, `BenignCaptureConservationSwitch` damaged low-decile and low-retail while preserving only low-volatility, and `PublicKyleLambdaFeasibilityBand` replayed `screen_0007` below the current `screen_0008` anchor. Future rounds should avoid causal/mass labels and Kyle/impact-band coefficients unless they introduce a different primary floor-risk owner with a mechanical no-release proof.
- Round 42 scratch lesson: public-dispersion, convexity, rank-stability, and continuity-shock labels did not advance retained state. `PublicSpreadDispersionEnvelope` damaged mean/leakage/floors, while `ExecutionCostConvexitySurface`, `CrossScenarioRankStabilityOwner`, and `RetailContinuityShockAbsorber` collapsed into generic uncertainty-label hidden release. Future rounds should stop feeding new labels into the existing downstream consumer path and instead test mechanical no-relief invariants or controlled downstream-consumer removal while preserving the `screen_0008` feasibility anchor.
- Round 43 scratch lesson: removing or isolating relief consumers was not enough. `FeasibilityReliefConsumerPruner` and `UnsafeDiscountBranchNullifier` improved leakage/selectivity only by overcharging and losing all floors, while `OneWayWidthMonotonicityAssembler` and `ProtectedPathConsumerIsolation` still collapsed into hidden release. Future rounds need a mechanism that preserves benign floor slices while retaining `screen_0008`'s leakage/selectivity gain, or the coordinator should record search saturation before spending more same-surface probes.
- Round 44 saturation gate: the proposer could not defend four genuinely distinct designs without replaying saturated basins under the current banned-family set. Continuing the same `screen_0008`-adjacent consumer/interface repair frame would be naming churn. The next productive move requires an operator-level search-frame change: deliberately relax one banned family with tight kill thresholds, authorize a fresh outside-literature import with new admissible mechanism classes, or change the seed / anchor frame.
- Round 45 scratch lesson: a fresh outside-mechanism reset was not sufficient. `ProperScoreReserveLedger` collapsed into reserve-score hidden release, `StableServiceMatchingKernel` and `ClearingPriorityWaterfall` were incumbent-equivalent or near-incumbent no-ops, and `SupplyFunctionServiceCurve` improved leakage/selectivity while losing mean and all tracked floors. Treat service-capacity shaping as a diagnostic only; do not coefficient-polish it without a hard no-floor-loss boundary, and do not import more market-design vocabulary unless the primary owner is mechanically distinct from labels, accounts, allocation, fee rights, and downstream relief.
- Round 46 scratch lesson: the narrow no-floor-loss service-capacity relaxation did not survive measurement. `IsofloorServiceSlopeSplitter` and `ProtectedSideServiceElasticity` were near-incumbent no-ops with floor loss versus `screen_0008`, `RetailFloorFirstServiceOwner` dragged every tracked floor and worsened leakage/selectivity, and `VolatilityIsoquantServiceMap` was incumbent-equivalent. Do not continue service-capacity curves, slope splitters, retail-floor gates, isoquant maps, or protected-side elasticity under the current `screen_0008` anchor; the next round needs either a different seed/anchor frame or a non-service primary owner mechanically distinct from labels, accounts, allocation, fee rights, downstream relief, and service gating.
- Round 47 scratch lesson: scratch-only retained-snapshot seeding did not break out. `SplitBusFeasibilityUnion` and `FirewallEventPathConjunction` improved leakage/selectivity only by overcharging and losing all tracked floors, while `SelectorFeasibilityCrosscheck` and `QuantileFirewallIngress` collapsed into hidden-release / floor-collapse basins. Do not keep unioning split-bus, feasibility, selector, tail, or firewall evidence across retained snapshots; those seed-frame recombinations are saturated under the current lane.
- Round 48 saturation gate: under the current ban set, proposer could not defend four genuinely distinct non-service, non-label primary owners without replaying saturated basins. Invariant/geometry holds, floor consensus, benign-capture caps, bandpass adjuncts, monotonicity proofs, and reserve-neutrality checks all map back to known failures. The next operator decision must either retire this retained lane and start a fresh run from a new seed/anchor frame, or explicitly relax one banned family for a tightly bounded diagnostic batch with concrete kill thresholds.
- May08 Round 1 scratch lesson: after seeding a fresh lane from `screen_0008`, post-WCEF sensor floors did not break out. `WENOShockSensor`, `SyndromeProtectedTripletCode`, `PhasePlaneCurlWitness`, and `BarrierCertificateRiskFloor` all routed new layer-1/2/3 evidence into the existing monotone / hazard / side-risk consumer path and collapsed into lower-fee hidden release with broken low-decile or low-retail floors; `MaxPlusRiskAssembler` was a sub-seed risk-composition reshuffle, and `ElasticEnergyReservoir` was phenotype-identical. Do not propose more WCEF-adjacent sensor floors unless the downstream consumer contract is mechanically changed so the signal cannot indirectly feed release, rebate, opportunity, refill, or calm paths.
- May08 Round 2 scratch lesson: consumer-contract isolation around WCEF also stayed below seed. `FeasibilityHoldOnlyBus` was nearest but still lowered fees, worsened leakage/selectivity, and missed seed; `DivergenceWriteLock` was a phenotype-identical no-op; `CalmProvenanceSeal` and `TypedSpreadAtomCutCap` overcharged into floor loss / benign-capture starvation; `CommitAfterPricingBarrier` and `KirchhoffCutDiode` collapsed into hidden release. Do not keep rearranging monotone evidence, calm provenance, cut eligibility, latent commit order, spread atoms, or divergence writes as primary owners under this seed.
- May08 Round 3 blocker: after Rounds 1-2, the proposer could not defend four genuinely distinct positive-expected designs without replaying saturated WCEF-adjacent sensor floors, consumer wiring, geometry-codec plateaus, state-write no-ops, direct fee / relief / spread-atom edits, or banned label families. The next productive move requires a search-frame change: fresh outside mechanism vocabulary or a different seed / anchor frame before more source work.
- May09 Round 1 scratch lesson: changing seed frame back to `screen_0007` / `QuantileTailRiskSketch` did not make tail consumer-right rewiring productive. `TailCutImmunityInvariant`, `ToxicSideCapFloorDecoupler`, and `CounterflowProofBeforeRelief` all improved or held leakage/selectivity only by over-tightening and losing mean/floors, while `ShortLongTailConsumerSplit` was a near miss below seed with worse leakage/selectivity and lower low-retail / low-volatility floors. Do not keep rearranging QTRS tail reserve, side cap/floor split, long-tail calm suppression, or relief-proof gates unless the proposal introduces a different primary owner outside tail consumer rights.
- May09 Round 2 scratch lesson: non-tail side-risk probes produced one tiny best-raw discard but did not approach breakout. `FlowShareEntropyRiskGate` advanced best raw to `screen_0002` at `487.57113729193804` but missed promotion margin, slightly worsened leakage/selectivity, and gave back low-decile / low-retail floors. `SlippageElasticityResponseOwner` was sub-seed, `ProtectionMassConservationRouter` collapsed into allocation-release hidden release, and `AdverseBenignOrthogonalBasis` replayed split-bus hidden release. Treat flow-share entropy as a weak measurement anchor only; do not keep polishing flow entropy, fixed-mass protection routing, adverse/benign classifier bases, or response-elasticity side-risk assembly without a new primary owner.
- May09 Round 3 scratch lesson: `VolatilityAccelerationCircuit` advanced best raw to `screen_0003` at `487.7145544914556`, but the gain is a risky overprotection profile: leakage/selectivity improved sharply while `time_weighted_mean_fee=0.00522064283762958` rose above the warning band and low-decile / low-retail fell versus QTRS. `AdverseDurationOccupancyBox` showed the same protection-vs-floor tradeoff in weaker form, `BenignMicrotradeSafeBand` was phenotype-near no-op, and `CreditStackExclusivityCompiler` over-tightened into floor loss. Future rounds should repair the acceleration anchor's low-decile / low-retail loss with a different primary owner, not polish acceleration pulse coefficients, duration occupancy, microtrade caps, or credit-stack exclusivity.
- May09 Round 4 scratch lesson: proposer/critic replacement was required before workers because the first batch only yielded two accepted designs. `MajorizationRiskVectorFilter` advanced best raw to `screen_0004` at `487.7232131981818`, but the lift was only `+0.0086587067261803` over `screen_0003` and still failed the floor-repair kill signature with `low_decile_mean_edge=371.5332084297802`, `low_retail_mean_edge=417.61900522444324`, and `time_weighted_mean_fee=0.005220196739061503`. `RiskMemoryAntiWindupIntegrator` was phenotype-identical to `screen_0003`, while `FalsePositiveProtectionScorecard` and `ShadowPriceConsensusBand` collapsed into hidden-release / overcharge floor failure. Future rounds should not continue false-positive scorecards, shadow consensus bands, vector-order side filters, or anti-windup memory writes without a new floor-preserving owner.
- May09 Round 5 saturation gate: QTRS-local search could not defend six non-replay candidates after excluding Round 1-4 families. Size/impact efficiency, counterflow proofs, hazard write backpressure, fee envelopes, reserve/service envelopes, and proper-score trust owners all mapped back to saturated response-elasticity, signed-impact, anti-windup/calm-barrier, direct-fee/final-compiler, geometry/service, or scorecard/consensus/robust-estimator families. The successor lane intentionally pivots to `screen_0005` as a floor-preserving seed frame; do not reopen QTRS-local source work unless the banned-family set is explicitly relaxed.
- May09 floor-seed Round 1 scratch lesson: new add-only control/safety evidence did not help the `screen_0005` seed. `KnockInSideInsurance` was exact phenotype replay, while `CUSUMInnovationSentinel`, `LyapunovDriftFloorOwner`, and `BarrierCertificateFloorOwner` collapsed into leakage/selectivity and floor failures. Continue to ban robust-demand / median-of-means and execution-price residual families, and do not route more process-control, Lyapunov, barrier-certificate, or side-insurance labels into the current hazard/side-risk consumers without a new downstream consumer contract.
- May09 floor-seed Round 2 scratch lesson: after a user-triggered entropy correction, OOD upstream/protection-sizing imports still failed under the `screen_0005` seed. `FixedReservoirObservationReadout`, `RecoveryHalfLifeHazardDecay`, `DangerTensorRiskDecomposition`, and `DangerSafeMemoryWriteMux` all collapsed into low-fee hidden release with high selectivity and broken floor slices; `SlowManifoldLatentProjector` improved only low-volatility while still missing seed mean and damaging low-decile / low-retail. Do not continue physical-reservoir readouts, recovery-half-life memory persistence, slow-manifold latent catch-up, danger-tensor decomposition, or danger/safe write-routing into the current hazard/protection path unless a future search-frame change supplies a new downstream owner that cannot become hidden release.
- May09 floor-seed Round 3 scratch lesson: web-search-backed OOD cut/recenter boundary controls did not help the `screen_0005` seed. `CutSolvencyFloorBudget`, `LeakyCutAdmissionMeter`, and `FloorBufferBeforeRecenter` collapsed into cut-budget or recenter starvation with high leakage/selectivity and broken floors; `LVRReadOnlyDrawdownSeal` was near-frontier but still lost mean and every tracked floor slice. Do not continue cut-solvency budgets, cut meters, aggregate cut caps, drawdown cut seals, or pre-recenter floor buffers under this seed unless the next proposal changes seed/search frame or proves the boundary preserves safe-side cuts and recentering without hidden release.
- May09 floor-seed Round 4 saturation gate: web-search-backed proposer passes using conformal risk, safe RL, sleeping experts, online constraints, conservative bandits, selective labels, and budgeted-resource vocabulary still could not defend four distinct designs. The critic rejected trust/admissibility gates, quote-mode selectors, permissive mode envelopes, predictive slack allocation, graph-credit estimators, delayed-label ledgers, component-regret attributors, adversarial context attributors, quorum witnesses, and seed-mode dominance samplers as replays of classifier/trust, layer-4 allocation-release, graph-gated estimator, selector polish, or attribution/source-label basins. The only narrowly accepted shape was `InstantConstraintExplorationArm + BaselineDominancePublicationTest + SleepingConstraintWitnessSet`, but it is a single witness-publication owner and cannot justify a four-design worker batch by itself. Do not continue this floor-seed lane under the current ban set; the next productive move requires a seed/search-frame change or exactly one explicitly relaxed family with predeclared kill thresholds.
- May09 floor-seed Round 6 scratch lesson: after the distilled trade-tox transplant advanced live best raw to `screen_0004` / `OracleTradeToxCoef6500` at `489.8573894977019`, local continuation around the trade-aligned toxicity-to-protection owner saturated below breakout. Activation gating, size tranching, side splitting, post-cut shield placement, and one coefficient split did not beat best raw; the nearest miss `TradeToxSplit7200` improved leakage/selectivity and low-decile only by giving up mean and lifting the fee band. Do not continue trade-tox activation/cap/split/coefficient/post-cut-shield tweaks unless the next proposal changes the owner contract beyond local protection-mass routing and proves it cannot replay opportunity/release/refill/recenter spending.
- May09 floor-seed Rounds 7-9 authorized oracle study: follow-up consumer-contract experiments reinforced the `oracle-consumer-contract-gap` already recorded in `docs/reference_oracle_evidence_cards.md`; no new candidate cleared the gates needed for canonical retention. Raw implementations and detailed summaries remain local-only. Do not reopen those oracle-inspired continuation families without fresh authorization and a mechanically new consumer contract.
- May09 floor-seed Round 10 scratch lesson: no-oracle, web-search-backed OOD add-only holds also failed on top of `OracleTradeToxCoef6500`. `PredicateTransformerFloorInvariant`, `CapabilityStampedProtectionFloor`, `AntichainContradictionHold`, `WaveletImpulseHoldBus`, `TukeyBiweightOutlierHold`, `MorphologicalCloseOpenFloorGuard`, `CountMinHeavyHitterToxicFlowHold`, and `EProcessSequentialHold` all failed smoke before screen consideration. Do not continue this family with smaller holds; the active `screen_0004` continuation tree now needs a fresh search frame, one explicitly relaxed family with kill thresholds, or a non-additive primary owner before quote-path hold logic.
- May09 floor-seed Round 11 retained lesson: no-oracle scratch measurement found `FlowDirectionalRisk280`, which beat `screen_0004` on screen, climb, and confirm and became canonical best raw as `screen_0005` at `490.75833078204124`. Its lift is a narrow flow-risk coefficient result with a small leakage/selectivity cost, not a new search frame; do not spend more coefficient-only polish or prefer second-order variants that fail holdout floor/leakage checks.
- May09 floor-seed Round 12 scratch lesson: a screen-capped consumer-boundary sweep tested flow-protection reserve, aligned-flow healing/refill gating, tail-only protection surcharge, and protected tail reserve around `screen_0005`. Reserve and optional-offset branches immediately replayed cut-boundary starvation at smoke, with low-decile falling to `222.85894799910943` and selectivity rising as high as `41.041092728283246`. Tail-only surcharge stayed near frontier at screen and marginally improved leakage/selectivity, but lost mean and low-decile / low-volatility edge versus `FlowDirectionalRisk280`. Do not continue these spend-back restrictions or tail surcharge coefficients; the next admissible refinement must preserve benign cuts through a different consumer contract.
- May09 floor-seed Round 13 retained lesson: under an explicitly relaxed screen-only search rule, lower event carry plus stronger passive recapture produced `screen_0006` / `Event140Recapture` at `491.910339497031`, beating `FlowDirectionalRisk280` by `+1.1520087149897336` while improving all tracked floor slices. Treat this as the active raw screen anchor; it has not been validated on `climb` or `confirm`.

## 08 Entry Format

When adding durable evidence, keep entries queryable:

```md
- `CandidateOrBasinName`
  - Tag: `positive-anchor` | `support-only` | `failure-basin` | `round-lesson`
  - Source: run id, round, and scratch or retained eval id.
  - Signal: metric movement versus live `best_raw` or named parked anchor.
  - Compatibility: when this evidence can be reused.
  - Collision: what proposal shape it should reject early.
  - Kill signature: concrete profile movement that ends follow-up.
```

Do not add round narration here unless the lesson remains useful after the round closes. Keep reusable critic questions in `docs/hill_climb.md`; keep this file focused on anchors, basin vocabulary, and decision routing.
