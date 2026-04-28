# apr21-screen490-1431 rounds 26-30

Run index: [apr21-screen490-1431.md](apr21-screen490-1431.md)

## Opening Constraints

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 25 closed with no canonical retained eval.
- Do not retune `ConstantProductCurvatureGuard` as a standalone primary idea. It may be used only as a bounded secondary adjunct after a distinct primary topology supplies new evidence.
- Avoid layer 5/6 release paths, final quote arbiters, estimator trust gates, split-bus / regime-selector polish, global fee-rent overlays, strict LVR floor tuning, broad latency-pressure protection, and reserve-band exhaustion protection.

## Round 26: Collision Splitter And Residual Curvature Adjunct

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 25 left `ConstantProductCurvatureGuard` as a positive but sub-best scratch anchor, not a standalone primary idea.

### Subagent Workflow

- Topology proposer supplied four layer 1-4 contracts:
  - `BatchCollisionObservationSplitter`
  - `SignedImpactResidualState`
  - `CurvatureResidualSpreadAdjunct`
  - `TwoRegimeFeeIntentSelector`
- Saturation critic rejected:
  - `SignedImpactResidualState` as too close to prior signed-impact / reconstructability / estimator-confidence failures.
  - `TwoRegimeFeeIntentSelector` as regime-selector / fee-band polish with high collision risk.
- Accepted worker batch:
  - `BatchCollisionObservationSplitter` as the primary layer 1 -> layer 3 observation splitter.
  - `CurvatureResidualSpreadAdjunct` only as a bounded secondary layer 4 shared-spread adjunct consuming local collision/residual evidence.
- Enforced entropy constraints:
  - zero layer 5/6 edits
  - no final quote arbiter, estimator trust gate, side protection magnitude edit, fee release, recapture/refill/opportunity/inventory path, split-bus polish, regime-selector polish, or standalone curvature coefficient tuning

### Accepted Probe Contracts

- `BatchCollisionObservationSplitter`
  - Layer mutation: layer 1 observation shaping into bounded layer 3 classification.
  - Interface boundary: split size-only clustered execution collision from price-informed movement; only a capped collision classification may influence `hazardObservation`.
  - Forbidden consumers: direct shared-spread adders, side protection magnitude, fee release, opportunity cuts, passive recapture/refill, inventory, and final quote assembly.
  - Kill signature: Round 25 protection-starvation replay, selectivity below `10`, low-retail / low-decile collapse, over-open selectivity above `24`, or failure to beat `screen_0005`.
- `CurvatureResidualSpreadAdjunct`
  - Layer mutation: local collision/residual evidence into a narrow layer 4 shared-spread adjunct.
  - Interface boundary: add only a capped shared-spread component when curve-depth residual and risk evidence agree.
  - Forbidden consumers: estimator selection, side protection magnitude, final quote arbitration, fee release, recapture/refill/opportunity, inventory, and all layer 5/6 paths.
  - Kill signature: exact LVR-floor no-op, pure curvature replay below `screen_0005`, fee lift without floor improvement, protection starvation, or failure to beat `screen_0005`.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round26/batch_collision_observation_splitter.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round26/curvature_residual_spread_adjunct.sol`

### Probe Results

- `BatchCollisionObservationSplitter`
  - Mean edge: `485.69403951152157`
  - Delta vs incumbent: `-0.22973119215026827`
  - Delta vs `screen_0005`: `-1.3183244509103815`
  - Key profile: `arb_loss_to_retail_gain=0.09935532675620504`, `quote_selectivity_ratio=21.223421763664202`, `time_weighted_mean_fee=0.0046814000052671735`
  - Floor slices: `low_decile_mean_edge=370.8653546741395`, `low_retail_mean_edge=415.7510736725755`, `low_volatility_mean_edge=463.1986733724692`
  - Outcome: killed as a near-frontier negative classifier; the split avoided protection-starvation and over-open collapse, but lost mean edge and did not clear the incumbent or best raw anchor.
- `CurvatureResidualSpreadAdjunct`
  - Mean edge: `485.9110489834109`
  - Delta vs incumbent: `-0.012721720260913116`
  - Delta vs `screen_0005`: `-1.1013149790210264`
  - Key profile: `arb_loss_to_retail_gain=0.0995096006435706`, `quote_selectivity_ratio=21.32550333010861`, `time_weighted_mean_fee=0.0046662251813338`
  - Floor slices: `low_decile_mean_edge=370.7069019006036`, `low_retail_mean_edge=415.88315825863646`, `low_volatility_mean_edge=463.32312640767236`
  - Outcome: killed as an almost no-op / sub-incumbent curvature adjunct. It preserved the incumbent band but did not reproduce Round 25's positive curvature signal and remained far below `screen_0005`.

### Decision

- No Round 26 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation and probe commands:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round26/batch_collision_observation_splitter.sol`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round26/curvature_residual_spread_adjunct.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round26/batch_collision_observation_splitter.sol > artifacts/scratch_probes/apr21-screen490-1431/round26/batch_collision_observation_splitter.json`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round26/curvature_residual_spread_adjunct.sol > artifacts/scratch_probes/apr21-screen490-1431/round26/curvature_residual_spread_adjunct.json`

### Updated Entropy Discipline

- Retire size-only collision splitting as implemented; it is safe but not productive enough to spend canonically.
- Retire residual-confirmed curvature as implemented; do not keep trying to recover `ConstantProductCurvatureGuard` through small residual gates.
- Round 27 needs a different primary interface, preferably outside collision/residual/curvature vocabulary:
  - layer 1 observation basis that changes the shape of raw evidence before hazard classification without reducing protection
  - layer 2 state memory with a non-scalar ownership contract, not estimator trust or signed-impact residual
  - layer 3 classifier that explicitly preserves low-retail and low-decile floors while avoiding direct fee-band or regime-selector polish

## Round 27: Floor-First Partition And Volume-Bucket Lattice

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 26 killed size-only collision splitting and residual-confirmed curvature recovery.

### Subagent Workflow

- Topology proposer supplied four topology/interface contracts:
  - `VolumeBucketImbalanceLattice`
  - `RetailFloorFirstStatePartition`
  - `AlternatingFlowNoiseShield`
  - `AsymmetricUncertaintyQuarantine`
- Saturation critic rejected:
  - `AlternatingFlowNoiseShield` because a layer 1 -> 4 shared-spread eligibility mask was too close to release / fee-band gating and collision/residual replay.
  - `AsymmetricUncertaintyQuarantine` because the ternary conflict state overlapped estimator trust / confidence-gate failures and lowered batch entropy.
- Accepted worker batch:
  - `RetailFloorFirstStatePartition` as the primary layer 2 -> layer 3 discrete floor-risk partition.
  - `VolumeBucketImbalanceLattice` only as a narrowed layer 1 -> layer 3 raw-evidence lattice with at least two nonlinear buckets and an explicit benign-capture cap.
- Enforced entropy constraints:
  - zero layer 5/6 edits
  - no final quote arbiter, shared-spread adder, direct fee release/compression, side opportunity, recapture/refill, inventory, split-bus polish, regime-selector coefficient polish, estimator trust gate, collision replay, or curvature recovery

### Accepted Probe Contracts

- `RetailFloorFirstStatePartition`
  - Layer mutation: layer 2 latent state into layer 3 bounded hazard/protection classification.
  - Interface boundary: export a discrete floor-risk partition that preserves protection in fragile states and leaves normal-state behavior near incumbent.
  - Forbidden consumers: direct fee-band movement, final quote selection, side opportunity, recapture/refill, inventory, split-bus polish, regime-selector coefficients, and all layer 5/6 paths.
  - Kill signature: failure to beat `screen_0005`, `low_decile_mean_edge < 370`, `low_retail_mean_edge < 415`, `quote_selectivity_ratio > 24`, selectivity below `10` with fee spike, or near-frontier no-op below both anchors.
- `VolumeBucketImbalanceLattice`
  - Layer mutation: layer 1 volume-time imbalance lattice into layer 3 capped classifier output.
  - Interface boundary: separate volume-bucket imbalance shapes before hazard classification; only a capped protection-preserving classifier output may feed hazard/protection floors.
  - Forbidden consumers: shared-spread adders, direct fee release/compression, final quote arbitration, side protection magnitude edits, inventory, recapture/refill/opportunity, and all layer 5/6 paths.
  - Kill signature: failure to beat `screen_0005`, protection-starvation replay, `quote_selectivity_ratio > 24`, `low_decile_mean_edge < 370`, or all floor slices falling together.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round27/retail_floor_first_state_partition.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round27/volume_bucket_imbalance_lattice.sol`

### Probe Results

- `RetailFloorFirstStatePartition`
  - Mean edge: `487.00001314499565`
  - Delta vs incumbent: `+1.0762424413238136`
  - Delta vs `screen_0005`: `-0.012350817436299621`
  - Key profile: `arb_loss_to_retail_gain=0.08387766865965202`, `quote_selectivity_ratio=16.081469460894738`, `time_weighted_mean_fee=0.005215796284264762`
  - Floor slices: `low_decile_mean_edge=370.4159098511467`, `low_retail_mean_edge=416.32788458867`, `low_volatility_mean_edge=464.1427325479601`
  - Outcome: killed by the predeclared `screen_0005` threshold. It is a strong positive scratch anchor versus incumbent and improves leakage/selectivity, low-retail, and low-volatility, but it misses the best raw retained discard by `0.012350817436299621` and lifts fees materially.
- `VolumeBucketImbalanceLattice`
  - Mean edge: `465.7270431957098`
  - Delta vs incumbent: `-20.19672750796201`
  - Delta vs `screen_0005`: `-21.285320766722123`
  - Key profile: `arb_loss_to_retail_gain=0.11139638280405637`, `quote_selectivity_ratio=20.020043550416148`, `time_weighted_mean_fee=0.005564242781167218`
  - Floor slices: `low_decile_mean_edge=320.9607255378222`, `low_retail_mean_edge=403.3132063178357`, `low_volatility_mean_edge=449.8219946402042`
  - Outcome: killed as fee-overcharge / floor-collapse despite acceptable overall selectivity. The nonlinear volume-bucket lattice did not replay over-open estimator behavior, but it overprotected enough to crush low-decile and low-retail slices.

### Decision

- No Round 27 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation and probe commands:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round27/retail_floor_first_state_partition.sol`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round27/volume_bucket_imbalance_lattice.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round27/retail_floor_first_state_partition.sol > artifacts/scratch_probes/apr21-screen490-1431/round27/retail_floor_first_state_partition.json`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round27/volume_bucket_imbalance_lattice.sol > artifacts/scratch_probes/apr21-screen490-1431/round27/volume_bucket_imbalance_lattice.json`

### Updated Entropy Discipline

- Preserve `RetailFloorFirstStatePartition` as a positive but non-promotable scratch anchor; future use needs a distinct primary topology or a fee-band-preserving variant, not a local floor-partition coefficient polish.
- Retire volume-bucket imbalance lattices that become broad protection floors. The failure mode was not over-open leakage; it was fee-overcharge with low-decile / low-retail damage.
- Round 28 should not run another classifier/protection-only batch. The next proposal needs a different outcome-space topology, ideally one that lowers the high-fee floor-first phenotype without using release/opportunity paths or weakening the protected floor slices.

## Round 28: Aged Evidence Premium Cap

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 27 preserved `RetailFloorFirstStatePartition` as a strong positive scratch anchor, but killed it for missing `screen_0005` and carrying a high-fee phenotype.

### Subagent Workflow

- Topology proposer supplied four candidate contracts:
  - `CohortNettingClassifier`
  - `FloorPremiumBudgetCap`
  - `AgingEvidenceLedger`
  - `SliceConditionalProtectionSwitchboard`
- Saturation critic rejected the batch as written because it was too concentrated in classifier/protection vocabulary after Round 27 explicitly closed with a warning against another classifier/protection-only batch.
- Critic rejected:
  - `CohortNettingClassifier` as renamed batch-collision / volume-bucket / route-quality evidence.
  - `SliceConditionalProtectionSwitchboard` as hidden floor-slice coupling and protection-only switching.
- Accepted worker contract:
  - `AgingEvidenceLedgerWithPremiumBudgetCap` as the only primary probe, narrowed to layer 2 evidence-lifetime ownership into a bounded layer 4 incremental-premium cap.
- Enforced entropy constraints:
  - no layer 5/6 edits
  - no final quote arbitration, per-slice branches, fee release/compression, opportunity/recapture/refill changes, inventory paths, split-bus polish, regime-selector polish, estimator trust gates, broad elapsed-gap hazard, direct side-protection magnitude edits, or support-signal stacking

### Accepted Probe Contract

- `AgingEvidenceLedgerWithPremiumBudgetCap`
  - Layer mutation: layer 2 adverse-evidence continuity into a bounded layer 4 incremental premium.
  - Interface boundary: maintain a short-lived adverse evidence ledger; the ledger may cap only a new incremental floor premium and must not lower incumbent base protection or change final quote selection.
  - Forbidden consumers: slice-conditionals, opportunity/recapture/refill, inventory, final quote selection, split-bus/regime-selector paths, and global fee-band movement.
  - Kill signature: `mean_edge <= 487.01236396243195` unless every floor slice materially clears `screen_0005`, `low_decile_mean_edge < 371.0`, `low_retail_mean_edge < 416.3`, `low_volatility_mean_edge < 464.0`, `quote_selectivity_ratio > 19.0`, `time_weighted_mean_fee > 0.00505`, or `time_weighted_mean_fee < 0.00466` with worse arb leakage.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round28/aging_evidence_ledger_with_premium_budget_cap.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round28/aging_evidence_post_cut_premium.sol`

### Probe Results

- `AgingEvidenceLedgerWithPremiumBudgetCap`
  - Mean edge: `407.3822230447608`
  - Delta vs incumbent: `-78.54154765891103`
  - Delta vs `screen_0005`: `-79.63014091719115`
  - Key profile: `arb_loss_to_retail_gain=0.25490350718832544`, `quote_selectivity_ratio=70.58714958601561`, `time_weighted_mean_fee=0.0036111885617042356`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=361.37180275293304`, `low_volatility_mean_edge=415.0876388835831`
  - Outcome: killed as an over-open release replay. The new premium expanded downstream behavior instead of preserving the floor-first leakage/selectivity band.
- `AgingEvidencePostCutPremium`
  - Mean edge: `407.3803014679076`
  - Delta vs incumbent: `-78.54346923576422`
  - Delta vs `screen_0005`: `-79.63206249452436`
  - Key profile: `arb_loss_to_retail_gain=0.25490704886796944`, `quote_selectivity_ratio=70.58838813138075`, `time_weighted_mean_fee=0.003611175373398958`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=361.37180275293304`, `low_volatility_mean_edge=415.08204884182834`
  - Outcome: killed as the same over-open release replay. Moving the premium after opportunity cuts did not change the phenotype, so the failure belongs to the aged-evidence premium topology as implemented, not just its first insertion point.

### Decision

- No Round 28 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation and probe commands:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round28/aging_evidence_ledger_with_premium_budget_cap.sol`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round28/aging_evidence_post_cut_premium.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round28/aging_evidence_ledger_with_premium_budget_cap.sol > artifacts/scratch_probes/apr21-screen490-1431/round28/aging_evidence_ledger_with_premium_budget_cap.json`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round28/aging_evidence_post_cut_premium.sol > artifacts/scratch_probes/apr21-screen490-1431/round28/aging_evidence_post_cut_premium.json`

### Updated Entropy Discipline

- Retire aged-evidence premium caps as implemented. Both variants landed in the same over-open release phenotype: very high selectivity, weak arb discipline, low fees, and broken low-decile / low-retail floors.
- Do not retry the Round 27 high-fee fix by adding another cap to floor-risk or evidence-age terms. It is behaving like a hidden release path rather than a fee-band-preserving layer 4 budget.
- Round 29 needs a primary topology outside classifier/protection/premium-cap vocabulary. Prefer a layer 1 raw observation transform or layer 2 state ownership change whose output cannot feed opportunity cuts, inventory, final quote selection, or shared fee compression.

## Round 29: Discrete Clearing Clock State

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 28 killed aged-evidence premium caps as hidden release paths.

### Subagent Workflow

- Topology proposer supplied four candidate contracts:
  - `DiscreteClearingClockState`
  - `RebalanceDebtStateAccount`
  - `BenignSizeInvariantNormalizer`
  - `FloorSliceBlindStateFirewall`
- Saturation critic narrowed the batch to one scratch worker:
  - Accepted `DiscreteClearingClockState` as the only sufficiently distinct primary interface: a temporal clearing-state ownership probe, not another floor partition, fee cap, reserve/LVR proxy, or size-bucket classifier.
  - Rejected `RebalanceDebtStateAccount` as too close to strict LVR floor / reserve-band exhaustion / protection-preservation support controls.
  - Rejected `BenignSizeInvariantNormalizer` as likely size/collision/volume-bucket normalization replay.
  - Rejected `FloorSliceBlindStateFirewall` as review doctrine rather than a scoring probe.
- Enforced entropy constraints:
  - one worker path only
  - no layer 5/6 edits
  - no final quote selection, opportunity cuts, inventory, recapture/refill, regime selector, split bus, aged-premium cap, broad fee compression, side-specific protection magnitude edit, or floor-slice conditional
  - normal/unknown clock state must remain incumbent-equivalent; all movement must come from the discrete clearing-clock classification boundary

### Accepted Probe Contract

- `DiscreteClearingClockState`
  - Layer mutation: layer 1 serial trade observations into a bounded layer 2 clearing-clock enum, consumed only by layer 3 classification.
  - Interface boundary: classify short-window stale-pickup / synchronized-clearing pressure; layer 4 may only preserve incumbent spread/protection in stale-pickup state, not add new spread or release fees.
  - Forbidden consumers: layer 5/6, final quote selection, opportunity cuts, inventory, recapture/refill, regime selector, split bus, aged-premium caps, broad fee compression, side-specific protection magnitude edits, and floor-slice conditionals.
  - Kill signature: `mean_edge < 485.92377070367183`, `quote_selectivity_ratio > 30`, `quote_selectivity_ratio < 10`, `time_weighted_mean_fee < 0.00420`, `time_weighted_mean_fee > 0.00520`, `arb_loss_to_retail_gain > 0.12`, `low_decile_mean_edge < 371.0`, `low_retail_mean_edge < 416.3`, `low_volatility_mean_edge < 464.0`, or failure to beat `screen_0005` without materially better floor slices.

### Probe Source

- `artifacts/scratch_probes/apr21-screen490-1431/round29/discrete_clearing_clock_state.sol`

### Probe Result

- `DiscreteClearingClockState`
  - Mean edge: `376.9252481330432`
  - Delta vs incumbent: `-108.99852257062863`
  - Delta vs `screen_0005`: `-110.08711582938875`
  - Key profile: `arb_loss_to_retail_gain=0.23917725270126566`, `quote_selectivity_ratio=33.17763415059683`, `time_weighted_mean_fee=0.007208990599378321`
  - Floor slices: `low_decile_mean_edge=225.2613187959861`, `low_retail_mean_edge=333.2531210964584`, `low_volatility_mean_edge=367.0478525214157`
  - Outcome: killed as temporal-clearing overprotection / protection-starvation. The topology did not replay Round 28's low-fee release; it instead drove fees and selectivity too high while breaking every tracked floor slice.

### Decision

- No Round 29 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation and probe commands:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round29/discrete_clearing_clock_state.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round29/discrete_clearing_clock_state.sol > artifacts/scratch_probes/apr21-screen490-1431/round29/discrete_clearing_clock_state.json`

### Updated Entropy Discipline

- Retire discrete clearing-clock classification as implemented. The interface was distinct, but short-window temporal pressure became another broad protection classifier and collapsed floors.
- Do not retry temporal clearing, collision, latency, or batch-pressure ideas unless the interface has an explicit cap that prevents fee overcharge and preserves benign retail capture before touching shared spread or hazard classification.
- Round 30 needs a different primary topology again, not a softened clearing-clock coefficient pass. Candidate families should avoid classifier/protection-only, premium-cap, LVR/reserve-preservation, volume/size/collision, and temporal batch-pressure vocabulary unless paired with a genuinely new upstream evidence owner and a hard no-overcharge boundary.
