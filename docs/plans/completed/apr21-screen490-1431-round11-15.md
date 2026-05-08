# apr21-screen490-1431 rounds 11-15

Run index: [apr21-screen490-1431.md](apr21-screen490-1431.md)

## Round 11: Upstream-Weighted Scratch Batch With One Layer-5 Exploit Slot

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round11/`
- Families explored:
  - `impact_backstopped_observation_partition.sol`
  - `classifier_export_split.sol`
  - `one_shot_event_carry_decoupler.sol`
  - `retail_floor_guarded_inventory_overlay.sol`

### Scaffold Precision

- `ImpactBackstoppedObservationPartition`
  - intended layer mutation: layer 1 observation shaping into layer 3 hazard/calm classifier
  - concrete goal: preserve the Round 10 retail / low-decile lift from size-vs-impact partitioning, but add a structural hazard floor so the classifier cannot drift into arb-leaky over-open behavior
- `ClassifierExportSplit`
  - intended layer mutation: layer 3 export ownership
  - concrete goal: let recentering see a slightly different quiet-confidence export while preventing that relaxed confidence from directly feeding passive recapture / refill eligibility
- `OneShotEventCarryDecoupler`
  - intended layer mutation: layer 4 shared event carry only
  - concrete goal: distinguish one-shot event cost from persistent clustered event carry without touching directional burst protection, side protection, or layer 6 opportunity logic
- `RetailFloorGuardedInventoryOverlay`
  - intended layer mutation: single exploit slot on layer 5 only
  - concrete goal: follow the tiny productive toxic-side inventory overlay once, but taper the overlay harder in quiet low-stress states to recover retail / low-retail giveback

### Probe Results

- Classifier-export branch: `ClassifierExportSplit`
  - Mean edge: `485.86047302151805`
  - Delta vs incumbent baseline: `-0.06329768215378`
  - Key profile: `arb_loss_to_retail_gain=0.09966753006928313`, `quote_selectivity_ratio=21.368513096048963`, `time_weighted_mean_fee=0.004664223927106644`
  - Floor slices: `low_decile_mean_edge=370.68209199419964`, `low_retail_mean_edge=415.8659450474437`, `low_volatility_mean_edge=463.24581427666325`
  - Outcome: safest branch of the round and close to the frontier, but it moved every tracked floor slice slightly negative and did not create a lift
- Observation/classifier branch: `ImpactBackstoppedObservationPartition`
  - Mean edge: `485.51849170798974`
  - Delta vs incumbent baseline: `-0.40527899568209`
  - Key profile: `arb_loss_to_retail_gain=0.10307779044591602`, `quote_selectivity_ratio=22.52139179598835`, `time_weighted_mean_fee=0.004576883674849245`
  - Floor slices: `low_decile_mean_edge=370.67743165221865`, `low_retail_mean_edge=415.6581678699094`, `low_volatility_mean_edge=462.91392991188737`
  - Outcome: informative discard; the hazard floor reduced but did not solve the Round 10 leak, and the prior low-decile / retail lift disappeared
- Shared-spread branch: `OneShotEventCarryDecoupler`
  - Mean edge: `482.8384820276922`
  - Delta vs incumbent baseline: `-3.08528867597962`
  - Key profile: `arb_loss_to_retail_gain=0.10863575034527075`, `quote_selectivity_ratio=24.016396955956324`, `time_weighted_mean_fee=0.004523399182002498`
  - Floor slices: `low_decile_mean_edge=368.72435232748955`, `low_retail_mean_edge=413.0413248810586`, `low_volatility_mean_edge=460.41718154456175`
  - Outcome: clear discard; reducing one-shot shared carry without any side/opportunity changes still lowered fees too broadly and replayed a milder over-open leak basin
- Layer-5 exploit branch: `RetailFloorGuardedInventoryOverlay`
  - Mean edge: `471.6739734737452`
  - Delta vs incumbent baseline: `-14.24979722992664`
  - Key profile: `arb_loss_to_retail_gain=0.12727240846406306`, `quote_selectivity_ratio=28.43620337350788`, `time_weighted_mean_fee=0.004475717337950919`
  - Floor slices: `low_decile_mean_edge=291.49310313012175`, `low_retail_mean_edge=397.89389952720693`, `low_volatility_mean_edge=463.4090105501336`
  - Outcome: clear discard; the quiet-state taper accidentally removed too much protection in the wrong states and collapsed into the over-open leak basin

### Decision

- No Round 11 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - quote-map outsider anchor: `width-skew-decoupled-quote-map`
  - best fresh layer-5-only anchor: `RetailGuardedInventoryToxicOverlay` / `RetailRecoveredInventoryOverlay` phenotype
- `contracts/src/StarterStrategy.sol` stays on the incumbent because:
  - the best Round 11 probe lost to the incumbent by `-0.06329768215378`
  - no probe improved a meaningful floor slice and mean edge together
  - the retained best raw `screen_0002` remains the only positive retained raw branch

### Updated Entropy Discipline

- Round 11 kept the search distribution upstream-heavy:
  - three probes targeted layers 1-4
  - only one probe used the layer-5 inventory exploit slot
  - no probe coupled a new signal into latent state, shared spread, side protection, and refill simultaneously
- Treat the exact layer 1/3 hazard-floor variant as exhausted:
  - the leak backstop protected less than needed
  - raising the backstop also erased the beneficial retail / low-decile movement, so the next observation-shaping probe should change the representation rather than just floor the same hazard value
- Treat layer 3 export splitting as a useful frontier-negative control:
  - it showed that quiet-confidence ownership can be separated without blowing up selectivity
  - but it is too small and floor-negative as implemented
- Treat layer 4 one-shot carry reduction as exhausted in this form:
  - merely lowering one-shot shared carry reopens arb flow even if directional burst and layer 6 are left untouched
  - a productive layer 4 retry must add a compensating persistent-event or toxicity discriminator, not just reduce shared event fee
- Pause the layer-5 inventory overlay for the immediate next batch:
  - the original tiny signal has now been cloned twice and the latest retail-recovery attempt failed badly
  - continuing to polish that seam would be entropy collapse unless a new non-inventory anchor first changes the frontier

### Next Batch Direction

- Keep the next batch outside layer 5/6 exploit polish unless one upstream branch creates a new anchor first.
- Prefer representation-level changes that do not route through the existing `quietGate` / `passiveRecaptureMemory` path:
  - observation shaping that separates volume participation, price impact, and latent divergence into independently bounded classifier inputs instead of one combined `volObservation`
  - hazard/calm ownership that produces typed exports for recentering, shared spread, and recapture eligibility without changing all three in one probe
  - layer 4 event classification that distinguishes toxic persistence from benign one-shot flow before changing event carry magnitude
- Do not spend the immediate next round on another layer-5 inventory taper or a layer-6 refill veto unless it is paired with a genuinely new upstream anchor from layers 1-4.

## Round 12: Upstream Representation Batch With No Inventory Exploit Clone

### Entropy Review Before Probing

- A read-only sidecar audit confirmed the saturated seams before source work:
  - direct quote-map / benign-width descendants
  - layer 5/6 inventory-refill exploit polish
  - event-carry magnitude reductions
  - standalone recenter / quiet export micro-tuning
  - broad state or budget memories that fan out through several downstream controls
- The batch was revised to keep the primary effort in layers 1, 3, and 4, with one non-inventory layer 5 diagnostic.
- No Round 12 branch touched `contracts/src/Reference.sol`, the retained lane, or `contracts/src/StarterStrategy.sol`.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round12/`
- Families explored:
  - `orthogonal_observation_basis.sol`
  - `typed_classifier_export_firewall.sol`
  - `toxic_persistence_event_classifier.sol`
  - `adverse_extension_floor_guard.sol`

### Scaffold Precision

- `OrthogonalObservationBasis`
  - intended layer mutation: layer 1 observation shaping into layer 3 classifier input basis
  - concrete goal: separate volume participation, price impact, and latent divergence into independently bounded hazard inputs while leaving shared spread, side protection, and refill logic unchanged
- `TypedClassifierExportFirewall`
  - intended layer mutation: layer 3 export ownership
  - concrete goal: split quiet/calm exports for recentering, shared-spread rebate, and recapture eligibility without changing downstream magnitudes
- `ToxicPersistenceEventClassifier`
  - intended layer mutation: layer 4 event classification
  - concrete goal: add carry only when clustered toxicity persists, instead of reducing one-shot event carry or replaying burst-allocation magnitude changes
- `AdverseExtensionFloorGuard`
  - intended layer mutation: layer 5 side-specific protection only
  - concrete goal: add a non-inventory floor guard for adverse extension / continuation states, with no inventory taper and no layer 6 refill changes

### Probe Results

- Observation-basis branch: `OrthogonalObservationBasis`
  - Mean edge: `485.9982070432665`
  - Delta vs incumbent baseline: `+0.07443633959468`
  - Key profile: `arb_loss_to_retail_gain=0.09876374478038706`, `quote_selectivity_ratio=21.09306433057808`, `time_weighted_mean_fee=0.004682285287359209`
  - Floor slices: `low_decile_mean_edge=370.87245460199745`, `low_retail_mean_edge=416.08020050217584`, `low_volatility_mean_edge=463.4622984122758`
  - Outcome: best branch of the round and the first non-layer-5 scratch branch in this late sequence to improve mean edge, leakage/selectivity, low-decile, low-retail, and low-volatility together; still below retained best raw `screen_0002` and too small for a canonical spend
- Classifier-export branch: `TypedClassifierExportFirewall`
  - Mean edge: `485.8598194566263`
  - Delta vs incumbent baseline: `-0.06395124704551`
  - Key profile: `arb_loss_to_retail_gain=0.09964731576725433`, `quote_selectivity_ratio=21.362911861413753`, `time_weighted_mean_fee=0.0046645006267726965`
  - Floor slices: `low_decile_mean_edge=370.68573115349`, `low_retail_mean_edge=415.86061754590077`, `low_volatility_mean_edge=463.24449082849117`
  - Outcome: safe frontier-negative control; export ownership can be separated without blowing up, but this formulation still moved floor slices slightly negative
- Event-classification branch: `ToxicPersistenceEventClassifier`
  - Mean edge: `482.9424322888383`
  - Delta vs incumbent baseline: `-2.98133841483354`
  - Key profile: `arb_loss_to_retail_gain=0.0861445133806136`, `quote_selectivity_ratio=16.223856842869427`, `time_weighted_mean_fee=0.005309743189608771`
  - Floor slices: `low_decile_mean_edge=367.05117719196267`, `low_retail_mean_edge=413.9046557553444`, `low_volatility_mean_edge=459.99529001626416`
  - Outcome: informative discard; toxic-persistence classification improved leakage/selectivity but over-tightened the book and damaged all floor slices
- Non-inventory layer-5 branch: `AdverseExtensionFloorGuard`
  - Mean edge: `460.7214466233637`
  - Delta vs incumbent baseline: `-25.20232408030813`
  - Key profile: `arb_loss_to_retail_gain=0.09711211721841577`, `quote_selectivity_ratio=14.110895936217828`, `time_weighted_mean_fee=0.006882066004693741`
  - Floor slices: `low_decile_mean_edge=346.7660686515812`, `low_retail_mean_edge=391.21522941229756`, `low_volatility_mean_edge=438.90406166848953`
  - Outcome: clear discard; side-specific adverse-extension protection over-tightened badly even without inventory coupling or layer 6 refill changes

### Decision

- No Round 12 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - quote-map outsider anchor: `width-skew-decoupled-quote-map`
  - best fresh upstream anchor: `OrthogonalObservationBasis`
- `contracts/src/StarterStrategy.sol` stays on the incumbent because:
  - `OrthogonalObservationBasis` improved the incumbent by only `+0.07443633959468`
  - it still trails retained best raw `screen_0002` by about `0.1600626045235`
  - the promotion margin from the retained screen spend remains much larger than this scratch signal

### Updated Entropy Discipline

- Round 12 successfully avoided the immediate entropy traps:
  - zero layer-5 inventory taper probes
  - zero layer-6 refill-veto probes
  - only one layer-5 branch, and it was non-inventory
  - three probes targeted layers 1-4
- Keep `OrthogonalObservationBasis` live as the new upstream scratch anchor:
  - unlike the cloned layer-5 overlay, it moved the frontier in several outcome metrics at once
  - the productive part appears to be representation basis separation, not another hazard floor on the same combined observation
- Treat typed export splitting as safe but still too small:
  - do not spend another standalone export firewall unless it is paired with a new representation basis or a specific floor-recovery mechanism
- Treat layer 4 persistence carry and non-inventory extension floor protection as currently over-tightening:
  - both improved leakage/selectivity but lost floor quality too broadly
  - do not retry them by adding more protective magnitude

### Next Batch Direction

- Keep exactly one follow-up on `OrthogonalObservationBasis` and make it about preserving the joint floor/mean lift while testing whether the hazard floor can be relaxed or shaped by persistence.
- Add at least two non-follow-up directions outside layer 1/3 representation:
  - a layer 3 typed export branch only if it consumes the new observation basis rather than repeating the old `quietGate` split
  - a layer 4 classifier branch that changes event labels without increasing carry magnitude
- Keep layer 5/6 exploit polish paused until a new upstream branch produces a larger anchor than `+0.074436`.

## Round 13: Scaffold-Balanced Scratch Batch With No Layer-5/6 Spend

### Entropy Review Before Probing

- A read-only sidecar reviewed the idea batch before implementation and found it scaffold-balanced after tightening:
  - accepted distribution: layer 1/3 follow-up, layer 3 export ownership, layer 2 latent-state update, and layer 4 event classification
  - zero layer 5/6 spend
  - main implementation risk: do not let the new observation basis become a hidden shared dependency that changes several downstream magnitudes at once
- The batch was tightened before source work:
  - `BasisTypedExportFirewall` was narrowed to `BasisOwnedClassifierExports`
  - `ImpactDominantDivergenceMemory` was narrowed to `ImpactDominantDivergenceUpdateGate`
  - `LabelOnlyBurstFirewall` was narrowed to `BenignOneShotBurstLabelFirewall`
- No Round 13 branch touched `contracts/src/Reference.sol`, the retained lane, or `contracts/src/StarterStrategy.sol`.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round13/`
- Families explored:
  - `persistence_shaped_observation_basis.sol`
  - `basis_owned_classifier_exports.sol`
  - `impact_dominant_divergence_update_gate.sol`
  - `benign_one_shot_burst_label_firewall.sol`
  - `persistence_weighted_participation_hazard.sol`

### Scaffold Precision

- `PersistenceShapedObservationBasis`
  - intended layer mutation: layer 1 observation shaping into layer 3 classifier input
  - concrete goal: keep the `OrthogonalObservationBasis` representation but shape only the hazard-floor contribution from persistence, without changing shared spread, side protection, or refill magnitudes
- `BasisOwnedClassifierExports`
  - intended layer mutation: layer 3 export ownership consuming the Round 12 observation basis
  - concrete goal: produce typed quiet exports for recentering, shared rebate, and recapture without repeating the old standalone `quietGate` split or changing downstream fee magnitudes
- `ImpactDominantDivergenceUpdateGate`
  - intended layer mutation: layer 2 latent-state update only
  - concrete goal: update the existing divergence memory more strongly only when impact dominates participation, with no new shock/debt/streak memory and no layer 5/6 coupling
- `BenignOneShotBurstLabelFirewall`
  - intended layer mutation: layer 4 event classification only
  - concrete goal: keep shared event carry unchanged, but prevent benign one-shot events from receiving the side-specific directional burst label
- `PersistenceWeightedParticipationHazard`
  - intended layer mutation: replacement layer 1/3 follow-up after the first persistence-shaped floor probe replayed the exact Round 12 phenotype
  - concrete goal: change participation-to-hazard weighting directly while still leaving shared spread, side protection, and refill magnitudes fixed

### Probe Results

- Observation-basis floor branch: `PersistenceShapedObservationBasis`
  - Mean edge: `485.9982070432665`
  - Delta vs incumbent baseline: `+0.07443633959468`
  - Delta vs retained best raw `screen_0002`: `-0.16006260452349`
  - Key profile: `arb_loss_to_retail_gain=0.09876374478038706`, `quote_selectivity_ratio=21.09306433057808`, `time_weighted_mean_fee=0.004682285287359209`
  - Floor slices: `low_decile_mean_edge=370.87245460199745`, `low_retail_mean_edge=416.08020050217584`, `low_volatility_mean_edge=463.4622984122758`
  - Outcome: exact replay of `OrthogonalObservationBasis`; the floor-shaping edit did not move the screen phenotype
- Layer 3 export branch: `BasisOwnedClassifierExports`
  - Mean edge: `471.5930606217411`
  - Delta vs incumbent baseline: `-14.33071008193076`
  - Key profile: `arb_loss_to_retail_gain=0.12671648397167976`, `quote_selectivity_ratio=28.171162846719646`, `time_weighted_mean_fee=0.004498092061770716`
  - Floor slices: `low_decile_mean_edge=291.36376925378426`, `low_retail_mean_edge=397.80069997773484`, `low_volatility_mean_edge=463.2144854206115`
  - Outcome: clear discard; even when consuming the new observation basis, typed export ownership reopened the book and replayed the high-selectivity / low-decile collapse
- Layer 2 update branch: `ImpactDominantDivergenceUpdateGate`
  - Mean edge: `485.95831415355934`
  - Delta vs incumbent baseline: `+0.03454344988751`
  - Delta vs retained best raw `screen_0002`: `-0.19995549423066`
  - Key profile: `arb_loss_to_retail_gain=0.09852494175179606`, `quote_selectivity_ratio=20.995431161840116`, `time_weighted_mean_fee=0.0046926848509245365`
  - Floor slices: `low_decile_mean_edge=370.5782423495196`, `low_retail_mean_edge=415.8867345909725`, `low_volatility_mean_edge=463.35724193974585`
  - Outcome: safe but weaker than the Round 12 observation anchor; improving leakage/selectivity and mean fee slightly did not preserve the floor slices
- Layer 4 label branch: `BenignOneShotBurstLabelFirewall`
  - Mean edge: `484.5979331883206`
  - Delta vs incumbent baseline: `-1.32583751535122`
  - Key profile: `arb_loss_to_retail_gain=0.10407848329739956`, `quote_selectivity_ratio=22.626289108510036`, `time_weighted_mean_fee=0.004599891869067222`
  - Floor slices: `low_decile_mean_edge=369.80074993678994`, `low_retail_mean_edge=414.60281624640623`, `low_volatility_mean_edge=461.96730827191857`
  - Outcome: informative discard; reducing side-specific burst labels for benign one-shot events reopened enough arb flow to damage every floor slice
- Replacement observation branch: `PersistenceWeightedParticipationHazard`
  - Mean edge: `485.9982070432665`
  - Delta vs incumbent baseline: `+0.07443633959468`
  - Delta vs retained best raw `screen_0002`: `-0.16006260452349`
  - Key profile: `arb_loss_to_retail_gain=0.09876374478038706`, `quote_selectivity_ratio=21.09306433057808`, `time_weighted_mean_fee=0.004682285287359209`
  - Floor slices: `low_decile_mean_edge=370.87245460199745`, `low_retail_mean_edge=416.08020050217584`, `low_volatility_mean_edge=463.4622984122758`
  - Outcome: second exact replay of `OrthogonalObservationBasis`; participation residual weighting is not an active enough screen-stage seam

### Decision

- No Round 13 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - quote-map outsider anchor: `width-skew-decoupled-quote-map`
  - best fresh upstream anchor: `OrthogonalObservationBasis`
- `contracts/src/StarterStrategy.sol` stays on the incumbent because:
  - the best Round 13 result is an exact replay of the Round 12 scratch anchor
  - the only non-replay positive branch, `ImpactDominantDivergenceUpdateGate`, improved the incumbent by only `+0.03454344988751`
  - every branch still trails retained best raw `screen_0002`

### Updated Entropy Discipline

- Round 13 avoided layer 5/6 exploit collapse:
  - zero inventory taper probes
  - zero refill-veto probes
  - zero direct layer 5/6 probes
- Retire direct micro-followups on `OrthogonalObservationBasis` hazard floors or participation residual weights:
  - two independently shaped variants replayed the exact same phenotype
  - more coefficient work on that layer 1/3 seam would be entropy collapse
- Treat `BasisOwnedClassifierExports` as evidence that typed quiet exports are still dangerous when they own recapture eligibility:
  - even with the new observation basis, the branch fell into the familiar over-open leak basin
  - do not retry typed exports unless recapture eligibility is explicitly held fixed or the branch removes recapture from the export change entirely
- Treat `ImpactDominantDivergenceUpdateGate` as a safe negative control:
  - existing divergence-memory update ownership can move leakage/selectivity safely
  - but it is too weak as a standalone lift and should not become another latent-state micro-tuning loop
- Treat layer 4 burst-label relaxation as exhausted in this form:
  - label-only reduction still reopened arb flow and damaged floors
  - future layer 4 work should add classification evidence before changing labels, not remove side burst labels on benign assumptions alone

### Next Batch Direction

- Do not spend the next batch on:
  - more `OrthogonalObservationBasis` hazard-floor or participation-weight variants
  - typed quiet export branches that change recapture eligibility
  - benign one-shot burst-label relaxation
  - layer 5/6 exploit polish
- Keep the best fresh upstream anchor as `OrthogonalObservationBasis`, but pause direct local polish until another interface creates a larger non-replay anchor.
- Productive next directions should be outside the saturated Round 13 seams:
  - layer 1 observation features that introduce genuinely new evidence, such as elapsed-time or route-quality partitioning, rather than reshaping the existing impact/participation residual
  - layer 3 classifier branches that change only hazard/calm classification and explicitly leave recapture eligibility fixed
  - layer 4 event evidence that adds a toxicity discriminator before side burst labels are changed, without reducing shared carry or broadening safe-side opportunity

## Round 14: Combination Idea Generation After Positive Scratch Anchors

### Positive Anchors To Combine

- Retained best raw anchor: `screen_0002` / `burst-pivot`
  - Mean edge: `486.15826964779`
  - Delta vs incumbent baseline: `+0.23449894411817`
  - Positive movement: lower `arb_loss_to_retail_gain`, lower `quote_selectivity_ratio`, higher `time_weighted_mean_fee`, higher `low_retail_mean_edge`, and higher `low_volatility_mean_edge`
  - Constraint: low-decile was weaker and the branch is a dangerous burst-neighbor, so it can only be used through a narrow admission gate, not as another broad burst surcharge clone
- Upstream representation anchor: `OrthogonalObservationBasis`
  - Mean edge: `485.9982070432665`
  - Delta vs incumbent baseline: `+0.07443633959468`
  - Positive movement: improved mean edge, leakage/selectivity, `time_weighted_mean_fee`, `low_decile_mean_edge`, `low_retail_mean_edge`, and `low_volatility_mean_edge` together
  - Constraint: Round 13 direct hazard-floor / participation-weight follow-ups replayed this exact phenotype, so do not spend more local OOB micro-polish
- Layer-5 protection anchor: `RetailGuardedInventoryToxicOverlay`
  - Mean edge: `485.97004692952817`
  - Delta vs incumbent baseline: `+0.04627622585633`
  - Positive movement: improved mean edge, leakage/selectivity, `time_weighted_mean_fee`, `low_decile_mean_edge`, and `low_volatility_mean_edge`
  - Constraint: it gave back slight retail / low-retail edge and has already been cloned, so it is allowed as exactly one exploit slot only
- Safe leakage-control anchor: `ImpactDominantDivergenceUpdateGate`
  - Mean edge: `485.95831415355934`
  - Delta vs incumbent baseline: `+0.03454344988751`
  - Positive movement: improved leakage/selectivity and `time_weighted_mean_fee`
  - Constraint: it was floor-negative versus both incumbent and OOB, so it should not be stacked with both OOB and layer-5 inventory in the same probe

### Entropy Review

- A read-only sidecar reviewed the draft batch after idea generation and rejected the triple `OrthogonalObservationBasis + ImpactDominantDivergenceUpdateGate + capped inventory overlay`.
- Rejection reason: the triple blend would combine weak / safe signals across layer 1/3, layer 2, and layer 5, making attribution poor while re-entering saturated inventory and latent-state seams.
- Accepted direction: combine previous positive anchors only where the touched interfaces stay separable and the expected outcome-space movement is distinct.
- Main anti-collapse constraints for this round:
  - do not make `OrthogonalObservationBasis` a hidden dependency for every probe
  - allow only one layer-5 inventory exploit slot
  - do not run another direct OOB hazard-floor or participation-weight variant
  - do not let burst handling become a reduced clone of `screen_0002`
  - keep recapture eligibility fixed in classifier branches

### Reviewed Round 14 Probe Plan

- `ElapsedGapHazardClassifier`
  - Layer mutation: layer 1 observation evidence into layer 3 hazard/calm classification
  - Combination logic: use the representation lesson from OOB, but introduce fresh elapsed-gap evidence instead of reshaping the same participation / impact residual
  - Outcome target: preserve the incumbent fee band while improving leakage/selectivity and floor slices without touching layer 5/6
  - Explicit exclusions: no OOB dependency, no recapture eligibility change, no side burst label change, no shared-carry magnitude change
- `OOBGuardedToxicInventoryOverlay`
  - Layer mutation: OOB layer 1/3 representation plus one narrow layer-5 toxic-side protection overlay
  - Combination logic: stack the two independently positive small-gain anchors while keeping overlay ownership strictly in side-specific protection
  - Outcome target: retain OOB's mean / low-retail lift while adding the inventory overlay's leakage and low-volatility protection
  - Explicit exclusions: no new inventory latent, no centering-support branch, no refill or calm-bonus coupling, no retail-recovery taper beyond the previously safe narrow overlay
- `OOBGatedShortGapCarryAdmission`
  - Layer mutation: OOB layer 1/3 representation plus a gated version of the retained best raw short-gap burst carry
  - Combination logic: test whether OOB evidence can admit only the profitable part of `screen_0002` while preserving the OOB floor lift
  - Outcome target: move toward retained best raw mean edge while avoiding the low-decile giveback and burst-neighbor over-search basin
  - Explicit exclusions: no broad burst magnitude increase, no benign one-shot burst-label relaxation, no safe-side opportunity broadening
- `RouteQualityCalmHazardPartition`
  - Layer mutation: fresh layer 1/3 classifier branch using stale-route / route-quality evidence
  - Combination logic: import a new classifier evidence source so the batch is not all OOB-dependent combinations
  - Outcome target: improve calm/hazard classification without moving downstream fee magnitudes
  - Explicit exclusions: no recapture eligibility change, no shared carry change, no layer 5/6 changes

### Continue This Round

- Implement scratch sources under `artifacts/scratch_probes/apr21-screen490-1431/round14/`.
- Validate each source before probing:
  - `uv run --isolated amm-match validate <scratch-source>`
- Probe each valid source without mutating the retained lane:
  - `uv run amm-match hill-climb probe --stage screen --json <scratch-source>`
- Keep `contracts/src/StarterStrategy.sol` on incumbent unless a probe creates a materially larger positive anchor than the existing scratch improvements.
- Do not spend a canonical retained eval until the probe result is clearly better than the tiny `+0.074436` OOB scratch signal and directionally closes the gap to retained best raw `screen_0002`.

### Source Tightening After Entropy Review

- A read-only sidecar found two hidden-coupling issues before probing:
  - `OOBGatedShortGapCarryAdmission` folded `shortGapBurst` into `eventSignal`, which would also raise directional burst fees and replay the saturated burst-neighbor seam.
  - `RouteQualityCalmHazardPartition` fed `calmRouteQuality` into global `calmMemory`, which would fan route-quality evidence into recentering, shared rebate, refill, and safe-side opportunity.
- Fixes applied before probing:
  - `OOBGatedShortGapCarryAdmission` now keeps short-gap admission as a separately capped shared carry term and leaves `directionalBurstFee` driven only by the base event signal.
  - `RouteQualityCalmHazardPartition` now tests stale-route hazard only and no longer globally boosts `calmMemory`.

### Probe Results

- Fresh elapsed-gap classifier: `ElapsedGapHazardClassifier`
  - Mean edge: `483.87111222487493`
  - Delta vs incumbent baseline: `-2.0526584787969`
  - Key profile: `arb_loss_to_retail_gain=0.08408764597525369`, `quote_selectivity_ratio=15.777785101448135`, `time_weighted_mean_fee=0.005329496214746635`
  - Floor slices: `low_decile_mean_edge=367.8263568715712`, `low_retail_mean_edge=414.65401493689933`, `low_volatility_mean_edge=460.6677666079411`
  - Outcome: informative discard; elapsed-gap evidence sharply reduced leakage/selectivity but over-tightened and damaged all floor slices.
- Tightened OOB short-gap carry branch: `OOBGatedShortGapCarryAdmission`
  - Mean edge: `485.4872359210837`
  - Delta vs incumbent baseline: `-0.43653478258812584`
  - Key profile: `arb_loss_to_retail_gain=0.09432271021525775`, `quote_selectivity_ratio=19.445576199318428`, `time_weighted_mean_fee=0.00485059991272276`
  - Floor slices: `low_decile_mean_edge=370.2528986956394`, `low_retail_mean_edge=415.53649198337206`, `low_volatility_mean_edge=463.03185523479186`
  - Outcome: tightened branch avoided the broad burst-fee replay but still lost mean edge and floor quality.
- Single layer-5 exploit slot: `OOBGuardedToxicInventoryOverlay`
  - Mean edge: `471.7199480389661`
  - Delta vs incumbent baseline: `-14.20382266470574`
  - Key profile: `arb_loss_to_retail_gain=0.12637524134210287`, `quote_selectivity_ratio=28.08583925602764`, `time_weighted_mean_fee=0.00449960708633554`
  - Floor slices: `low_decile_mean_edge=291.37139122454005`, `low_retail_mean_edge=398.0070430879104`, `low_volatility_mean_edge=463.40503053778104`
  - Outcome: clear discard; the inventory overlay recombination replayed the over-open leak / low-decile collapse despite the upstream OOB anchor.
- Tightened route-quality branch: `RouteQualityCalmHazardPartition`
  - Mean edge: `485.8278385928236`
  - Delta vs incumbent baseline: `-0.0959321108482527`
  - Key profile: `arb_loss_to_retail_gain=0.09955056308899776`, `quote_selectivity_ratio=21.283875628632842`, `time_weighted_mean_fee=0.004677276113898826`
  - Floor slices: `low_decile_mean_edge=370.5490640515928`, `low_retail_mean_edge=415.8369730582601`, `low_volatility_mean_edge=463.149703071685`
  - Outcome: closest branch of the round after tightening, but still frontier-negative and slightly floor-negative.

### Decision

- No Round 14 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - best fresh upstream scratch anchor: `OrthogonalObservationBasis`
- `contracts/src/StarterStrategy.sol` stays on the incumbent because:
  - every Round 14 probe lost to the incumbent
  - the closest branch was still `-0.0959321108482527`
  - none of the branches improved mean edge and floor slices together

### Updated Entropy Discipline

- Treat elapsed-gap hazard/calm evidence as an over-tightening trap unless paired with an explicit floor-preservation mechanism that does not raise carry broadly.
- Treat OOB plus short-gap burst admission as currently negative; the profitable part of `screen_0002` was not recovered by this gating shape.
- Retire OOB plus inventory overlay recombination for the immediate future; the layer-5 inventory anchor has now failed as a stackable adjunct.
- Keep route-quality hazard as a near-frontier negative control only; at most one future branch may make a softer route-hazard refinement, and it must not route through global calm or downstream opportunity.

### Round 15 Starting Constraints

- Keep layer 5/6 at zero unless an upstream branch creates a new larger anchor.
- Avoid direct OOB follow-ups, gap-style over-tightening, typed-export recapture ownership, and inventory-overlay recombination.
- Rebalance toward layers 1-4 with distinct interfaces:
  - one soft route-hazard refinement only if it stays classifier-local
  - one layer-2 flow-memory ownership branch
  - one layer-4 shared-spread/rebate safety branch
  - one representation branch that changes participation or impact evidence without using the OOB template

## Round 15: Layer 1-4 Rebalance After Round 14 Negative Controls

### Previous-Round Takeaways

- Round 14 confirmed that elapsed-gap hazard evidence is not automatically productive; it reduced leakage and selectivity but over-tightened enough to lose more than `2` mean-edge points.
- Route-quality hazard was the closest fresh branch at `-0.0959321108482527`, but it was still slightly floor-negative and must stay a narrow classifier-local refinement if retried.
- OOB-dependent combinations are now saturated for this span:
  - OOB plus short-gap carry lost to the incumbent.
  - OOB plus inventory overlay collapsed into the known over-open / low-decile failure basin.
- No Round 15 probe should touch layer 5 or layer 6. The goal is to find a cleaner upstream anchor before any downstream exploit slot returns.

### Draft Probe Plan

- `SoftRouteHazardClassifier`
  - Layer mutation: layer 1 observation evidence into layer 3 hazard/calm classification
  - Interface boundary: soften the Round 14 stale-route hazard weights with no layer 5/6 formula edits; route evidence may affect downstream behavior only through the existing `hazardMemory` path
  - Outcome target: recover the small route-quality classification signal without the floor giveback from over-tightening
  - Explicit exclusions: no OOB basis, no global calm boost, no recapture/refill/opportunity terms, no elapsed-gap carry
- `FlowOwnershipMemorySplit`
  - Layer mutation: layer 2 latent flow-memory ownership only
  - Interface boundary: reduce cross-side memory bleed after long gaps while preserving same-side flow pressure; leave `flowPressure` alpha, quiet gate, side protection, shared spread, inventory gates, refill formulas, and opportunity formulas untouched
  - Outcome target: improve side classification and leakage/selectivity without changing the fee band directly
  - Explicit exclusions: no new inventory state, no recapture eligibility change, no burst/event magnitude change
- `CappedLeakageRebateSuppression`
  - Layer mutation: layer 4 shared spread/rebate only
  - Interface boundary: keep the existing shared-spread formula but cap/suppress the existing calm rebate under narrow leakage proxies so quiet rebates do not reopen arb flow
  - Outcome target: reduce over-open leakage while preserving low-decile and low-retail floors better than elapsed-gap carry increases
  - Explicit exclusions: no added spread, no event carry increase, no directional protection change, no side-specific inventory overlay, no refill/opportunity change

### Entropy Review Request

- Ask a read-only sidecar to review the draft before source work.
- Rework or drop any branch that:
  - is another OOB clone
  - smuggles route/calm evidence into downstream layer 5/6 behavior
  - turns shared-spread safety into a broad fee increase
  - changes more than one interface without clean attribution

### Entropy Review Outcome

- The sidecar accepted `SoftRouteHazardClassifier` only as the single route-quality retry, with the wording tightened to acknowledge that `hazardMemory` naturally propagates through existing downstream formulas.
- The sidecar accepted `FlowOwnershipMemorySplit` as genuinely distinct, provided it remains memory ownership only and does not tune `flowPressure`, quiet gate, spread, side protection, inventory gates, refill, or opportunity formulas.
- The sidecar accepted `CappedLeakageRebateSuppression` as distinct but risky, so it is limited to suppressing the existing calm rebate under narrow leakage proxies.
- `ParticipationOnlyVolBasis` was dropped because the participation/impact split is too close to the saturated OOB replay seam.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round15/`
- Families explored:
  - `soft_route_hazard_classifier.sol`
  - `flow_ownership_memory_split.sol`
  - `capped_leakage_rebate_suppression.sol`

### Probe Results

- Layer 4 capped rebate branch: `CappedLeakageRebateSuppression`
  - Mean edge: `485.9341580084984`
  - Delta vs incumbent baseline: `+0.010387304826565469`
  - Delta vs retained best raw `screen_0002`: `-0.22411163929158`
  - Key profile: `arb_loss_to_retail_gain=0.09959679527229486`, `quote_selectivity_ratio=21.354987851871723`, `time_weighted_mean_fee=0.004663865695599794`
  - Floor slices: `low_decile_mean_edge=370.70436631364066`, `low_retail_mean_edge=415.9331432876122`, `low_volatility_mean_edge=463.3402788602685`
  - Outcome: tiny but clean support-only positive; it improved leakage/selectivity and all tracked floors without changing downstream formulas, but the signal is too small for a retained spend.
- Layer 2 flow-memory branch: `FlowOwnershipMemorySplit`
  - Mean edge: `485.5862838988102`
  - Delta vs incumbent baseline: `-0.3374868048616122`
  - Key profile: `arb_loss_to_retail_gain=0.09957118330410578`, `quote_selectivity_ratio=21.26151669366217`, `time_weighted_mean_fee=0.004683164646188523`
  - Floor slices: `low_decile_mean_edge=370.15178719261826`, `low_retail_mean_edge=415.50600553217976`, `low_volatility_mean_edge=462.9637703421113`
  - Outcome: informative discard; cleaner flow ownership lowered leakage/selectivity but lost too much floor and mean edge.
- Soft route-hazard branch: `SoftRouteHazardClassifier`
  - Mean edge: `485.92377070367183`
  - Delta vs incumbent baseline: `0`
  - Key profile: `arb_loss_to_retail_gain=0.09961822784430861`, `quote_selectivity_ratio=21.366983876018754`, `time_weighted_mean_fee=0.004662250340166877`
  - Floor slices: `low_decile_mean_edge=370.69865470550553`, `low_retail_mean_edge=415.9137203431734`, `low_volatility_mean_edge=463.32099611706855`
  - Outcome: exact no-op versus incumbent; soft route hazard was too weak after removing the over-coupled calm path.

### Decision

- No Round 15 candidate earned a canonical spend.
- `CappedLeakageRebateSuppression` is a support-only positive anchor, not a promotable branch:
  - it improved every tracked metric slightly
  - it still trails retained best raw `screen_0002` by about `0.22411163929158`
  - it is far below promotion-margin scale
- The retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - best fresh upstream scratch anchor: `OrthogonalObservationBasis`
  - newest support-only positive anchor: `CappedLeakageRebateSuppression`

### Round 16 Starting Constraints

- Close this chunk after Round 15 and continue in `apr21-screen490-1431-round16-20.md`.
- Keep `CappedLeakageRebateSuppression` as a support control only; do not stack it with OOB, inventory overlays, or burst admission in the next batch.
- Retire the soft route-hazard retry for now; one exact no-op after one near-frontier negative is enough.
- Retire pure flow cross-memory reduction for now; it moved leakage in the right direction but damaged floor quality.
- Round 16 should import a new upstream topology outside OOB, route/gap hazard, flow-memory ownership, and layer 5/6 inventory.
