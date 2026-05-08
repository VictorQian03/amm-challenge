# apr21-screen490-1431 rounds 06-10

Run index: [apr21-screen490-1431.md](apr21-screen490-1431.md)

## Round 6: Narrow Interface Batch Across Ratchet Confidence, Passive Recapture Decomposition, And Impact Relief

### Probe Sources

- Scratch sources live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round6/`
- Families explored:
  - `ratchet_confidence_veto.sol`
  - `passive_recapture_decomposition.sol`
  - `transient_impact_relief_router.sol`

### Probe Results

- Latent-motion confirmation branch: `RatchetConfidenceVeto`
  - Mean edge: `485.4635121216384`
  - Delta vs incumbent baseline: `-0.46025858203343`
  - Key profile: `arb_loss_to_retail_gain=0.09906465148863941`, `quote_selectivity_ratio=20.94606653874535`, `time_weighted_mean_fee=0.00472951097073013`
  - Floor slices: `low_decile_mean_edge=370.26113207325625`, `low_volatility_mean_edge=462.75840885783276`
  - Outcome: effectively a rerun of the earlier `LatentRatchetRecenter` frontier anchor, not a new branch; the narrowed veto framing produced the same phenotype and no new lift
- Downstream decomposition branch: `PassiveRecaptureDecomposition`
  - Mean edge: `485.7580855240307`
  - Delta vs incumbent baseline: `-0.16568517964113`
  - Key profile: `arb_loss_to_retail_gain=0.09966968767878888`, `quote_selectivity_ratio=21.341891099503428`, `time_weighted_mean_fee=0.004670143203996948`
  - Floor slices: `low_decile_mean_edge=370.5757310547956`, `low_retail_mean_edge=415.75413574863165`, `low_volatility_mean_edge=463.1167764771204`
  - Outcome: closest fresh non-quote-map branch so far in the thin run; almost baseline-identical, but still weaker overall and not worth a canonical spend
- Impact-routing branch: `TransientImpactReliefRouter`
  - Mean edge: `471.4540560300042`
  - Delta vs incumbent baseline: `-14.46971467366763`
  - Key profile: `arb_loss_to_retail_gain=0.13175560915523565`, `quote_selectivity_ratio=29.98987185374273`, `time_weighted_mean_fee=0.004393336850447148`
  - Floor slices: `low_decile_mean_edge=362.60708347087075`, `low_retail_mean_edge=404.44819898612536`, `low_volatility_mean_edge=449.44124692431546`
  - Outcome: clear discard; lowering shared average fee without a hard enough persistence clamp reopened too much safe-side flow and re-entered the known over-open leak basin

### Decision

- No Round 6 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - structurally different outsider anchor: `width-skew-decoupled-quote-map`
  - best fresh non-quote-map anchor: `PassiveRecaptureDecomposition`
- `contracts/src/StarterStrategy.sol` stays on the incumbent because every Round 6 branch was either weaker than baseline or merely reproduced an existing frontier anchor.

### Updated Entropy Discipline

- Treat `RatchetConfidenceVeto` as a useful negative control, not a live new family:
  - the latent-motion seam still matters
  - but this specific confidence-veto formulation did not create a new phenotype beyond `LatentRatchetRecenter`
- Keep `PassiveRecaptureDecomposition` live as the best fresh downstream-decomposition anchor:
  - it stayed near the frontier without crossing into quote-map reopening or whole-loop rewrites
  - but it still failed to produce even a small floor lift, so the next follow-up must make an explicit promise on downside improvement instead of settling for baseline imitation
- Treat `TransientImpactReliefRouter` as an exhausted variant of the impact-relief seam:
  - lower shared average fee by itself is not a win here
  - when persistence control stays too weak, the branch simply reopens the book, pushes `quote_selectivity_ratio` toward `30`, and degrades the floor slices
- The core decomposition lesson from Round 6 is:
  - narrow downstream rewiring is safer than whole-loop rewrites
  - but merely matching the incumbent profile is not enough; the next live branches must still target a specific bottleneck with measurable expected movement

### Next Batch Direction

- Keep exactly one live follow-up on the `PassiveRecaptureDecomposition` seam:
  - preserve its near-baseline `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, and mean-fee band
  - target a small lift in `low_decile_mean_edge` or `low_volatility_mean_edge` without broadening the reopen path
- Re-admit the explicit inventory-asymmetry idea, but only if it touches inventory centering and side skew directly:
  - do not let a new inventory memory fan out into refill, calm bonus, or other benign-flow controls in the same probe
- If the impact family is revisited, require a stronger persistence clamp:
  - burst-cost relief cannot be admitted again unless it keeps `quote_selectivity_ratio` near the incumbent band instead of drifting into the `30` range
- Do not spend the next round on another latent/quote crossover, medium-anchor rewrite, or whole-loop topology remap.

## Round 7: Scaffold-Disciplined Batch Across Inventory Centering, Passive Coordination, And Recenter Release

### Probe Sources

- Scratch sources live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round7/`
- Families explored:
  - `inventory_skew_centering_overlay.sol`
  - `passive_coordination_floor_clamp.sol`
  - `recenter_release_confirmation.sol`

### Scaffold Precision

- `InventorySkewCenteringOverlay`
  - intended layer mutation: add a dedicated inventory-asymmetry latent, then feed it only into layer 5 side-centering / protection
  - rejected decomposition: no refill, calm-bonus, or shared-spread coupling from the new inventory signal
- `PassiveCoordinationFloorClamp`
  - intended layer mutation: layer 6 only
  - concrete goal: keep the existing layer 5 centering output fixed, then stop layer 6 from spending the same calm / passive support twice through both inventory centering and refill reopening
- `RecenterReleaseConfirmation`
  - intended layer mutation: layer 2/3 boundary only
  - concrete goal: test whether post-recenter divergence release was still a live bottleneck once the probe stopped leaking into layer 6 calm bonus logic

### Probe Results

- Inventory-centering branch: `InventorySkewCenteringOverlay`
  - Mean edge: `407.397316621976`
  - Delta vs incumbent baseline: `-78.52645408169582`
  - Key profile: `arb_loss_to_retail_gain=0.25485831363595646`, `quote_selectivity_ratio=70.5664372114863`, `time_weighted_mean_fee=0.0036116080633651773`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=361.39622833965785`, `low_volatility_mean_edge=415.09194433735433`
  - Outcome: immediate collapse into the known low-fee / high-selectivity leak basin; even when inventory asymmetry was kept out of refill and shared spread, feeding it into centering support alone still reopened the book too far
- Passive-coordination branch: `PassiveCoordinationFloorClamp`
  - Mean edge: `485.55343698120186`
  - Delta vs incumbent baseline: `-0.3703337224699794`
  - Key profile: `arb_loss_to_retail_gain=0.09952039704134599`, `quote_selectivity_ratio=21.24405220281422`, `time_weighted_mean_fee=0.004684624011052017`
  - Floor slices: `low_decile_mean_edge=370.0882268455382`, `low_retail_mean_edge=415.4665362553595`, `low_volatility_mean_edge=462.87437142391104`
  - Outcome: stayed in the incumbent frontier band and slightly improved leakage/selectivity, but every floor slice moved the wrong way; useful evidence that pure refill coordination is safer than new state additions, but still not a lift
- Recenter-release branch: `RecenterReleaseConfirmation`
  - Mean edge: `485.9237712840134`
  - Delta vs incumbent baseline: `+0.0000005803415774607856`
  - Key profile: `arb_loss_to_retail_gain=0.0996182215325847`, `quote_selectivity_ratio=21.36698137883322`, `time_weighted_mean_fee=0.004662250589653695`
  - Floor slices: `low_decile_mean_edge=370.69865508272073`, `low_retail_mean_edge=415.91372069425887`, `low_volatility_mean_edge=463.3209964823145`
  - Outcome: exact no-op relative to the incumbent; once the probe was kept strictly on the layer 2/3 boundary, the remaining bottleneck was too small to move the phenotype at all

### Decision

- No Round 7 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - structurally different outsider anchor: `width-skew-decoupled-quote-map`
  - best fresh downstream-decomposition anchor: `PassiveRecaptureDecomposition`
- `contracts/src/StarterStrategy.sol` stays on the incumbent because Round 7 produced one no-op, one safe-but-weaker frontier neighbor, and one full collapse into a known exhausted basin.

### Updated Entropy Discipline

- Treat the direct inventory-latent idea as exhausted in its current form:
  - the probe was scaffold-disciplined
  - but the outcome shows that adding inventory asymmetry to centering support alone is still enough to regenerate the old reopen / leak basin
- Treat post-recenter divergence-release tuning as exhausted as a standalone seam:
  - once isolated from layer 6, it produced no measurable phenotype change
  - do not spend more turns renaming that same latent-release adjustment
- Keep refill coordination as the only Round 7 seam that remained near the frontier:
  - it did not improve the floor
  - but it did confirm that the remaining productive search surface is still on the layer 5 / layer 6 boundary, not in new state loops or latent recenter micro-tuning
- The precise decomposition lesson from Round 7 is:
  - the incumbent already roughly instantiates the six-layer scaffold
  - the remaining defect is that layer 5 protection and layer 6 recapture still share too much support through `passiveRecaptureMemory` and `inventoryCenteringOffset`
  - productive follow-ups should further separate those interfaces, not add another state variable or another cross-layer gate

### Next Batch Direction

- Keep exactly one live follow-up on the passive-coordination seam:
  - require an explicit positive promise on `low_decile_mean_edge` or `low_volatility_mean_edge`
  - prefer redirecting saved refill budget into a narrow toxic-side floor clamp rather than merely shrinking refill more
- Do not spend the immediate next round on:
  - direct inventory-latent additions
  - post-recenter release-only tweaks
  - any new design that lets a fresh signal fan out across latent state, centering, and refill in the same probe
- If inventory is revisited later, bind it to a narrowly defined layer 5 toxic-side protection term instead of a general centering-support magnitude.

## Round 8: Boundary-Focused Batch Across Passive Reinvestment, Share Handoff, And Layer-5 Inventory Protection

### Probe Sources

- Scratch sources live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round8/`
- Families explored:
  - `passive_floor_reinvestment.sol`
  - `centering_share_handoff.sol`
  - `inventory_toxic_floor_overlay.sol`

### Scaffold Precision

- `PassiveFloorReinvestment`
  - intended layer mutation: layer 5 / layer 6 boundary only
  - concrete goal: keep the split passive-support shape from Round 6 / Round 7, then redirect coordination-suppressed refill support into a narrow toxic-side floor clamp instead of letting it disappear
- `CenteringShareHandoff`
  - intended layer mutation: layer 5 / layer 6 boundary only
  - concrete goal: keep `inventoryCenteringOffset` as a layer 5 output, but stop passing the raw offset into layer 6 opportunity / refill logic; layer 6 should only see normalized consumed-width share
- `InventoryToxicFloorOverlay`
  - intended layer mutation: layer 5 only
  - concrete goal: revisit inventory asymmetry as an instantaneous toxic-side protection overlay, with no new latent, no shared-spread coupling, and no refill / calm-bonus fan-out

### Probe Results

- Passive-reinvestment branch: `PassiveFloorReinvestment`
  - Mean edge: `435.64521313861746`
  - Delta vs incumbent baseline: `-50.27855756505437`
  - Key profile: `arb_loss_to_retail_gain=0.19633711331404358`, `quote_selectivity_ratio=47.41707104054788`, `time_weighted_mean_fee=0.004140641946149506`
  - Floor slices: `low_decile_mean_edge=234.15422937769358`, `low_retail_mean_edge=397.5101577393552`, `low_volatility_mean_edge=414.74916293463866`
  - Outcome: immediate collapse into the old reopen / leak basin; redirecting coordination-suppressed refill support back into a toxic-side floor clamp still reopened too much safe-side flow and cratered the floor
- Share-handoff branch: `CenteringShareHandoff`
  - Mean edge: `485.3641070564707`
  - Delta vs incumbent baseline: `-0.55966364720111`
  - Key profile: `arb_loss_to_retail_gain=0.09944338240989212`, `quote_selectivity_ratio=21.162547165965144`, `time_weighted_mean_fee=0.004699027089225953`
  - Floor slices: `low_decile_mean_edge=370.3500200882793`, `low_retail_mean_edge=415.40290740446983`, `low_volatility_mean_edge=462.64325702396695`
  - Outcome: safe frontier neighbor, but still weaker overall and floor-negative; fully severing raw centering output from layer 6 is structurally clean, yet too restrictive on benign recapture by itself
- Layer-5 inventory branch: `InventoryToxicFloorOverlay`
  - Mean edge: `485.9664374967119`
  - Delta vs incumbent baseline: `+0.04266679304008`
  - Key profile: `arb_loss_to_retail_gain=0.09927653956364338`, `quote_selectivity_ratio=21.254235159583853`, `time_weighted_mean_fee=0.004670906236721395`
  - Floor slices: `low_decile_mean_edge=370.7389001321591`, `low_retail_mean_edge=415.8652497162579`, `low_volatility_mean_edge=463.4095295789166`
  - Outcome: best branch of the round; it slightly improved overall edge plus `low_decile_mean_edge` and `low_volatility_mean_edge` while also improving leakage/selectivity, but the gain is tiny, retail edge slipped slightly, and it still trails the retained best raw

### Decision

- No Round 8 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - quote-map outsider anchor: `width-skew-decoupled-quote-map`
  - best fresh layer-5-only anchor: `InventoryToxicFloorOverlay`
- `contracts/src/StarterStrategy.sol` stays on the incumbent because:
  - `InventoryToxicFloorOverlay` improved the incumbent only by `+0.04266679304008` mean edge, far below any spend-worthy signal
  - it still underperforms the existing best raw `screen_0002`
  - the other two Round 8 branches either degraded the frontier slightly or collapsed into an exhausted basin

### Updated Entropy Discipline

- Treat passive-floor reinvestment as exhausted in its current form:
  - even without a new latent or shared-spread rewrite, redirecting suppressed refill budget into a toxic-side clamp still regenerated the low-fee / high-selectivity leak basin
  - do not spend another round on that seam without a materially different ownership model
- Treat pure share handoff as a useful negative control, not a live spend candidate:
  - it preserved the incumbent band on leakage/selectivity
  - but it worsened mean edge and every tracked floor slice, so raw separation alone is not enough
- Keep `InventoryToxicFloorOverlay` live as the new best fresh anchor:
  - the inventory idea only became productive once it was expressed as a narrow layer 5 toxic-side protection term
  - the productive part was not new state or centering support magnitude; it was strict layer ownership
- The precise decomposition lesson from Round 8 is:
  - layer 5 / layer 6 separation still matters
  - but the next lift is more likely to come from a narrow layer 5 protection improvement than from broader layer 6 budget redistribution
  - when a boundary fix is admitted, it should preserve current refill behavior as much as possible and only veto obvious double-spend or amplification, not reprice the whole downstream path

### Next Batch Direction

- Keep exactly one live follow-up on the `InventoryToxicFloorOverlay` seam:
  - preserve layer 5 ownership only
  - protect the small `low_decile_mean_edge` / `low_volatility_mean_edge` lift while recovering the slight `retail_edge` / `low_retail_mean_edge` giveback
- If the layer 5 / layer 6 boundary is revisited again, make it a narrower amplification veto:
  - let layer 6 see consumed-width share only as a cap or veto on extra refill amplification
  - do not remove raw recapture support wholesale the way `CenteringShareHandoff` did
- Do not spend the immediate next round on:
  - another passive-budget reinvestment clamp
  - another direct inventory latent or centering-support overlay
  - any redesign that re-couples inventory, refill, and calm bonus in the same probe

## Round 9: Interface-Separated Scratch Batch Across Layer-5 Inventory, Refill Amplification, And Burst Allocation

### Probe Sources

- Scratch sources live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round9/`
- Families explored:
  - `retail_guarded_inventory_toxic_overlay.sol`
  - `consumed_width_refill_amplification_veto.sol`
  - `persistent_burst_allocation_clamp.sol`

### Scaffold Precision

- `RetailGuardedInventoryToxicOverlay`
  - intended layer mutation: layer 5 only
  - concrete goal: follow the Round 8 inventory toxic-side overlay exactly once, then taper the extra protection in quiet / low-stress states to recover some retail giveback without adding inventory memory, centering support, shared-spread coupling, or refill coupling
- `ConsumedWidthRefillAmplificationVeto`
  - intended layer mutation: narrow layer 5 / layer 6 boundary only
  - concrete goal: keep raw passive recapture and current refill support intact, then let consumed centering width act only as a cap on extra refill amplification
- `PersistentBurstAllocationClamp`
  - intended layer mutation: layer 4 / layer 5 event allocation only
  - concrete goal: separate transient one-shot burst handling from persistent burst cost without adding safe-side opportunity relief

### Probe Results

- Layer-5 inventory branch: `RetailGuardedInventoryToxicOverlay`
  - Mean edge: `485.97004692952817`
  - Delta vs incumbent baseline: `+0.04627622585633`
  - Key profile: `arb_loss_to_retail_gain=0.09924081919356585`, `quote_selectivity_ratio=21.24118605231934`, `time_weighted_mean_fee=0.004672094060525857`
  - Floor slices: `low_decile_mean_edge=370.7289199400079`, `low_retail_mean_edge=415.8796161659957`, `low_volatility_mean_edge=463.43136571767974`
  - Outcome: best branch of the round and a small improvement over both the incumbent and the Round 8 inventory overlay on mean edge / low-volatility floor; still too small to spend canonically, still trails `screen_0002`, and still gives back a little retail / low-retail edge versus the incumbent
- Refill-amplification branch: `ConsumedWidthRefillAmplificationVeto`
  - Mean edge: `485.92264588372365`
  - Delta vs incumbent baseline: `-0.00112481994819`
  - Key profile: `arb_loss_to_retail_gain=0.09962321671227459`, `quote_selectivity_ratio=21.36722779723432`, `time_weighted_mean_fee=0.004662430599685439`
  - Floor slices: `low_decile_mean_edge=370.7233071679516`, `low_retail_mean_edge=415.9241978886293`, `low_volatility_mean_edge=463.32578064435364`
  - Outcome: near no-op with slight floor / low-retail lift but no mean lift; useful negative control that a pure amplification veto is safe but not a standalone improvement
- Burst-allocation branch: `PersistentBurstAllocationClamp`
  - Mean edge: `470.7093157746327`
  - Delta vs incumbent baseline: `-15.21445492903911`
  - Key profile: `arb_loss_to_retail_gain=0.14568914723650767`, `quote_selectivity_ratio=36.465395176111336`, `time_weighted_mean_fee=0.003995271312237125`
  - Floor slices: `low_decile_mean_edge=360.52018576552746`, `low_retail_mean_edge=402.01257218054246`, `low_volatility_mean_edge=448.8585090322258`
  - Outcome: clear discard; despite the cleaner allocation framing, it reopened too much safe-side flow and replayed the known over-open leak basin

### Decision

- No Round 9 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - quote-map outsider anchor: `width-skew-decoupled-quote-map`
  - best fresh layer-5-only anchor: `RetailGuardedInventoryToxicOverlay`
- `contracts/src/StarterStrategy.sol` stays on the incumbent because:
  - `RetailGuardedInventoryToxicOverlay` improved the incumbent by only `+0.04627622585633` mean edge
  - the signal is smaller than the existing retained best raw `screen_0002`
  - the branch still has a small retail / low-retail giveback

### Updated Entropy Discipline

- Keep `RetailGuardedInventoryToxicOverlay` as the live narrow layer-5 anchor:
  - the productive part is still strict toxic-side protection ownership, not inventory state, centering support, or refill coupling
  - the remaining bottleneck is recovering retail / low-retail edge while preserving the tiny low-decile and low-volatility lift
- Treat `ConsumedWidthRefillAmplificationVeto` as a safe negative control:
  - narrow layer 6 vetoes can preserve the floor
  - but they are unlikely to unlock the next lift alone unless paired with a separate positive layer-5 signal
- Retire `PersistentBurstAllocationClamp` and do not immediately revisit burst allocation:
  - even a cleaner persistent/transient split fell into the `quote_selectivity_ratio=36+` over-open basin
  - this confirms that burst handling remains a risky neighbor of the retained best raw, not the next primary interface
- Round 9 avoided entropy collapse by admitting exactly one inventory-overlay descendant and keeping the other probes on distinct layer boundaries. Do not turn the next batch into three variants of the layer-5 inventory overlay just because it is now the best fresh scratch anchor.

### Next Batch Direction

- If the layer-5 inventory anchor is followed, keep it as the single exploit slot and make the change about retail recovery only:
  - no new inventory latent
  - no centering-support magnitude branch
  - no refill / calm bonus coupling
- Add at least two non-inventory directions before another inventory-heavy batch:
  - classifier-local benign-flow recovery that changes observation / hazard partitioning without touching shared spread or layer 6
  - a narrow layer 6 opportunity-cut conservation branch that preserves refill behavior but prevents only obvious amplification into leak states
- Reject any next branch that broadly lowers `time_weighted_mean_fee`, pushes `quote_selectivity_ratio` above the incumbent band, or spends multiple interfaces to chase a sub-`0.1` mean-edge scratch gain.

## Round 10: Rebalanced Scaffold Batch Across Layers 1-5

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round10/`
- Families explored:
  - `benign_impact_partition_classifier.sol`
  - `calm_recenter_partition.sol`
  - `persistent_event_carry_partition.sol`
  - `retail_recovered_inventory_overlay.sol`

### Scaffold Precision

- `BenignImpactPartitionClassifier`
  - intended layer mutation: layer 1 observation shaping into layer 3 hazard/calm classifier
  - concrete goal: separate size-only benign participation from real spot/divergence impact before it becomes hazard, without touching shared spread, side protection, or layer 6 refill
- `CalmRecenterPartition`
  - intended layer mutation: layer 2/3 latent recenter interface
  - concrete goal: let quiet recentering use a local flow-isolation gate instead of passing the full shared `quietGate` through latent state and downstream recapture
- `PersistentEventCarryPartition`
  - intended layer mutation: layer 4 shared-spread event carry
  - concrete goal: move shared event carry toward persistent clustered events, not one-shot impact, while leaving directional burst protection unchanged
- `RetailRecoveredInventoryOverlay`
  - intended layer mutation: single exploit slot on layer 5 only
  - concrete goal: follow the Round 9 toxic-side inventory overlay once, but taper the extra layer-5 protection in quiet low-stress states to recover retail / low-retail giveback

### Probe Results

- Observation/classifier branch: `BenignImpactPartitionClassifier`
  - Mean edge: `484.68877960683574`
  - Delta vs incumbent baseline: `-1.23499109683609`
  - Key profile: `arb_loss_to_retail_gain=0.10805606088976281`, `quote_selectivity_ratio=24.17575204688496`, `time_weighted_mean_fee=0.004469604944665447`
  - Floor slices: `low_decile_mean_edge=371.08311454426183`, `low_retail_mean_edge=415.1475933335432`, `low_volatility_mean_edge=461.7709703107428`
  - Outcome: informative discard; layer 1/3 partitioning recovered retail edge and low-decile edge, but it lowered average fees too far, leaked arb, and hurt low-volatility quality
- Latent/classifier branch: `CalmRecenterPartition`
  - Mean edge: `485.6208080212544`
  - Delta vs incumbent baseline: `-0.30296268241743`
  - Key profile: `arb_loss_to_retail_gain=0.09943272096222323`, `quote_selectivity_ratio=21.20127934906851`, `time_weighted_mean_fee=0.004689939664730273`
  - Floor slices: `low_decile_mean_edge=370.5524559482856`, `low_retail_mean_edge=415.5564615448508`, `low_volatility_mean_edge=462.847236604277`
  - Outcome: frontier-neighbor discard; the isolated recenter gate improved leakage/selectivity slightly but moved every tracked floor slice the wrong way
- Shared-spread branch: `PersistentEventCarryPartition`
  - Mean edge: `480.3409097080189`
  - Delta vs incumbent baseline: `-5.58286099565291`
  - Key profile: `arb_loss_to_retail_gain=0.10308388680211865`, `quote_selectivity_ratio=21.318661065602075`, `time_weighted_mean_fee=0.004835382789046062`
  - Floor slices: `low_decile_mean_edge=365.6162464612346`, `low_retail_mean_edge=410.1941464169518`, `low_volatility_mean_edge=457.9422870066972`
  - Outcome: clear discard; layer 4 persistence-weighted shared carry over-tightened the book and damaged all floor slices without buying enough leakage improvement
- Layer-5 exploit branch: `RetailRecoveredInventoryOverlay`
  - Mean edge: `485.96999779469746`
  - Delta vs incumbent baseline: `+0.04622709102563`
  - Key profile: `arb_loss_to_retail_gain=0.09924105033187047`, `quote_selectivity_ratio=21.241260463293898`, `time_weighted_mean_fee=0.004672088575127857`
  - Floor slices: `low_decile_mean_edge=370.7288910097623`, `low_retail_mean_edge=415.87957042121894`, `low_volatility_mean_edge=463.4313186684187`
  - Outcome: best branch of the round, but effectively a reproduction of the Round 9 layer-5 overlay; the quiet-state retail taper did not materially recover the retail / low-retail giveback and the gain remains too small to spend canonically

### Decision

- No Round 10 candidate earned a canonical spend.
- The retained lane remains:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - quote-map outsider anchor: `width-skew-decoupled-quote-map`
  - best fresh layer-5-only anchor: `RetailGuardedInventoryToxicOverlay` / `RetailRecoveredInventoryOverlay` phenotype
- `contracts/src/StarterStrategy.sol` stays on the incumbent because:
  - the best Round 10 probe improved the incumbent by only `+0.04622709102563`
  - it still trails retained best raw `screen_0002`
  - all layer 1-4 probes were negative despite producing useful decomposition evidence

### Updated Entropy Discipline

- The round corrected the search distribution away from a layer 5/6-only exploit trap:
  - three of four probes touched layers 1-4
  - only one probe followed the current layer-5 inventory anchor
  - no probe changed latent state, shared spread, side protection, and refill in the same source
- Treat the layer 1/3 partition as a live diagnostic, not a spend candidate:
  - it exposed a real upstream knob that can lift retail and low-decile behavior
  - but the current implementation fell into a mild over-open leak basin by pushing `quote_selectivity_ratio` to `24.18` and `arb_loss_to_retail_gain` to `0.1081`
- Treat the layer 2/3 recenter isolation as a near-frontier negative control:
  - it improved leakage/selectivity slightly
  - but it lost every floor slice, so standalone recenter throttling is not the missing bottleneck
- Treat the layer 4 persistent carry partition as exhausted in this form:
  - moving shared event carry toward persistence raised average fees and damaged floor quality
  - do not retry layer 4 by simply adding more shared carry; any layer 4 follow-up needs to separate event carry from benign low-volatility capture more cleanly
- The layer-5 inventory overlay remains the best fresh scratch phenotype, but it is now a tiny repeated signal rather than a reason to collapse the next batch into more inventory variants.

### Next Batch Direction

- Keep layer 1-4 exploration active next round; do not retreat back into only layer 5/6 because the best scratch score lives there.
- Good next upstream directions:
  - layer 1 observation partition with an explicit arb-leak backstop, preserving the retail / low-decile lift from `BenignImpactPartitionClassifier` while keeping `quote_selectivity_ratio` near the incumbent band
  - layer 3 hazard/calm classifier that changes benign-state confidence without feeding the same gate into layer 6 refill
  - layer 4 event allocation that reduces one-shot shared carry without lowering mean fee broadly or damaging low-volatility slices
- If one exploit slot is admitted, keep it to a single layer-5 toxic-side overlay follow-up and require a concrete retail / low-retail recovery target, not another sub-`0.05` mean-edge clone.
