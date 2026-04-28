# apr21-screen490-1431 rounds 16-20

Run index: [apr21-screen490-1431.md](apr21-screen490-1431.md)

## Round 16: New Upstream Topology After Route/OOB/Inventory Saturation

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0002` at `486.15826964779`.
- Breakout target: `490`.
- Latest support-only positive anchor: `CappedLeakageRebateSuppression` at `+0.010387304826565469`.
- Latest rejected seams:
  - OOB short-gap and OOB inventory recombinations
  - elapsed-gap over-tightening
  - route-quality hazard retry
  - pure flow cross-memory reduction

### Round 16 Search Constraints

- Keep layer 5/6 at zero for the first Round 16 batch.
- Do not use OOB, route/gap hazard, typed export recapture ownership, burst admission, or inventory overlay motifs.
- Import at least two genuinely new upstream/topology ideas instead of polishing Round 14/15 near misses.
- Any support use of `CappedLeakageRebateSuppression` must stay isolated and cannot be stacked with another small anchor in the same probe.

### Pre-Review Draft Probe Plan

- `SignedImpactConsistencyClassifier`
  - Layer mutation: layer 1 trade-direction observation into layer 3 hazard classification
  - Interface boundary: add hazard evidence only when trade direction, observed price movement, and latent divergence agree; do not change calm memory, flow memory, spread, side protection, or opportunity formulas
  - Outcome target: reduce arb leakage by distinguishing directional adverse selection from benign large participation without using OOB or gap evidence
  - Explicit exclusions: no OOB participation split, no route/gap hazard, no layer 4-6 edits
- `TailCompressedObservation`
  - Layer mutation: layer 1 observation shaping only
  - Interface boundary: compress only the extreme tail of `volObservation` before hazard/calm classification; leave flow, spread, side protection, and opportunity formulas untouched
  - Outcome target: recover floor slices from over-tightened elapsed-gap/event branches while measuring whether the incumbent overreacts to rare observation tails
  - Explicit exclusions: no calm boost, no shared rebate change, no downstream protection/opportunity edits
- `ReversionHazardVeto`
  - Layer mutation: layer 3 hazard/calm classification
  - Interface boundary: use movement toward the latent spot only as a bounded hazard-veto signal; do not increase `calmMemory`, change recentering, recapture eligibility, refill, or opportunity formulas
  - Outcome target: identify benign mean-reversion states without broad quiet-state opportunity reopening
  - Explicit exclusions: no passive recapture changes, no safe-side refill changes, no inventory centering changes

### Entropy Review Request

- Ask a read-only sidecar to review before source work.
- Drop or tighten any branch that:
  - reproduces OOB participation/impact splitting
  - uses gap/route evidence under a new name
  - routes calm evidence into layer 5/6 behavior too broadly
  - creates a broad fee-band change instead of an upstream classifier test

### Entropy Review Outcome

- The sidecar accepted `SignedImpactConsistencyClassifier` as the strongest keep because signed trade-direction evidence is outside the OOB/route/gap neighborhood.
- The sidecar rejected `TailCompressedObservation` because replacing global `volObservation` would fan out into hazard, flow, event carry, spread, quiet/calm, and opportunity gates.
- `ReversionVelocityClassifier` was tightened to `ReversionHazardVeto`:
  - it may only damp hazard when price movement is converging toward latent spot
  - it must not increase calm memory or touch recentering, passive recapture, refill, inventory, or opportunity formulas

### Reviewed Round 16 Probe Plan

- `SignedImpactConsistencyClassifier`
  - Layer mutation: layer 1 trade-direction observation into layer 3 hazard classification
  - Boundary after review: bounded classifier evidence only; no `volObservation`, `flowPulse`, `eventSignal`, spread coefficient, calm, recentering, recapture, refill, inventory, or opportunity changes
- `ReversionHazardVeto`
  - Layer mutation: layer 3 hazard veto only
  - Boundary after review: damp the current hazard observation under convergence evidence; no calm boost and no downstream formula edits

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round16/`
- Families explored:
  - `signed_impact_consistency_classifier.sol`
  - `reversion_hazard_veto.sol`

### Probe Results

- Signed trade-direction classifier: `SignedImpactConsistencyClassifier`
  - Mean edge: `485.92377070367183`
  - Delta vs incumbent baseline: `0`
  - Key profile: `arb_loss_to_retail_gain=0.09961822784430861`, `quote_selectivity_ratio=21.366983876018754`, `time_weighted_mean_fee=0.004662250340166877`
  - Floor slices: `low_decile_mean_edge=370.69865470550553`, `low_retail_mean_edge=415.9137203431734`, `low_volatility_mean_edge=463.32099611706855`
  - Outcome: exact no-op; the bounded signed-impact evidence did not activate enough to move the screen phenotype.
- Reversion hazard-veto classifier: `ReversionHazardVeto`
  - Mean edge: `485.0895641827317`
  - Delta vs incumbent baseline: `-0.8342065209401426`
  - Key profile: `arb_loss_to_retail_gain=0.10134707012970552`, `quote_selectivity_ratio=21.807634055602264`, `time_weighted_mean_fee=0.004647320744254235`
  - Floor slices: `low_decile_mean_edge=370.37764451813086`, `low_retail_mean_edge=415.1697287223503`, `low_volatility_mean_edge=462.5906576437133`
  - Outcome: clear discard; hazard damping on reversion evidence reopened leakage and damaged floors.

### Decision

- No Round 16 candidate earned a canonical spend.
- The retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - best fresh upstream scratch anchor: `OrthogonalObservationBasis`
  - support-only positive anchor: `CappedLeakageRebateSuppression`

### Updated Entropy Discipline

- Treat signed-impact evidence as too weak in bounded classifier-only form; do not repeat without a stronger independent activation test.
- Treat reversion hazard damping as unsafe for now; it moved in the over-open direction and weakened floor slices.
- Round 17 should not spend on scalar hazard dampers or small classifier evidence terms alone. The next batch needs either:
  - a new external topology, or
  - a structural separation that changes the interface contract rather than another small additive classifier term.

### Round 17 Starting Constraints

- Do not spend on another small additive classifier term, scalar hazard damper, route/gap hazard, OOB participation split, flow-memory ownership tweak, or layer 5/6 inventory/recapture branch.
- Require at least one idea imported from outside the current strategy's local vocabulary before source work.
- Prefer a structural interface change with clear ownership, such as:
  - an explicit two-channel hazard representation where adverse-selection protection and benign-flow fee capture consume different bounded signals
  - a seed- or regime-conditioned estimator that changes only observation interpretation, not downstream spread/protection formulas
  - a public-score/profile-relative normalizer anticipation signal that remains upstream and does not directly change layer 5/6 opportunity
- Keep `CappedLeakageRebateSuppression` as a support-only control and do not combine it until a larger primary anchor exists.
- Do not inspect `Reference.sol`, `ReferenceStrategy.sol`, or any oracle/reference implementation unless the active task explicitly authorizes it. Use only public score/profile surfaces and sanitized phenotype targets.

### Apr 23 Authorized Oracle Phenotype Calibration

- The external oracle probe was authorized for analysis only and was scored through `hill-climb probe`, not retained `eval`.
- Screen profile: `mean_edge=535.6745798276557`, `arb_loss_to_retail_gain=0.05164343636902818`, `quote_selectivity_ratio=13.608817574261822`, `time_weighted_mean_fee=0.0037948511020311367`, `low_decile_mean_edge=412.73546803287235`, `low_retail_mean_edge=459.6027208846513`, `low_volatility_mean_edge=508.674622016504`.
- Use those values as phenotype targets only. Do not inspect or copy oracle/reference implementation details in future rounds unless the active task explicitly re-authorizes that surface.

### Round 17 Subagent Operating Note

- Use at least one topology proposer before source work. It should propose topology/interface contracts, not local terms inside the current latent-state quote engine.
- Use at least one saturation/entropy critic before implementation. It should screen for renamed incumbent vocabulary, hidden coupling, support-signal reuse, weak-attribution stacking, and missing kill signatures.
- Use at least one strategy worker after the critic accepts a bounded plan. The worker owns scratch sources only, should not mutate retained ledgers, and combines implementation with review: validate, run `hill-climb probe`, inspect artifacts, reflect, and make bounded refinements until the local idea reaches saturation.
- The main agent is the coordinator by default. It owns synthesis, active-note updates, and any selected canonical retained `eval`; do not spawn a separate coordinator subagent for that role.
- Each proposed candidate must state: changed interface, owner layer, allowed consumers, forbidden consumers, expected phenotype movement, invariants that must stay near the incumbent band, and kill signature.
- The batch must include at least one candidate outside incumbent vocabulary. If all candidates are OOB, route/gap hazard, flow ownership, inventory overlay, burst admission, recenter release, quiet refill, or scalar hazard-damper variants, reject the batch before writing Solidity.

## Round 17: Upstream Information/Liquidity Split Bus

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard before the round: `screen_0002` at `486.15826964779`.
- Breakout target: `490`.
- Round 16 killed small additive classifier terms and scalar hazard dampers:
  - signed-impact evidence was an exact no-op
  - reversion hazard damping reopened leakage and damaged floor slices

### Sidecar Review Outcome

- Topology proposer recommended structural upstream interfaces rather than local coefficient polish:
  - `InformationLiquiditySplitBus`
  - `DepthQuantileObservationDecoder`
  - `ProfileTargetShadowNormalizer`
- Entropy critic accepted a scratch-only batch if it:
  - kept at least two candidates upstream or mid-scaffold
  - included at least one outside incumbent vocabulary
  - avoided OOB, route/gap hazard, flow ownership, inventory overlay, burst admission, quiet refill, passive recapture, and scalar hazard damping
  - declared allowed consumers, forbidden consumers, invariants, and kill signatures before source work

### Accepted Probe Contracts

- `InformationLiquiditySplitBus`
  - Layer mutation: layer 1 observation shaping into layer 3 hazard evidence.
  - Interface boundary: split raw observation into `liquidityDemand` and `informationStress`; allow information stress into hazard/spread/protection and liquidity demand into flow/observation interpretation only.
  - Forbidden consumers: no calm boost, recentering, refill, inventory, passive recapture, or layer 5/6 opportunity changes.
  - Expected movement: reduce leakage/selectivity while preserving or lifting floor slices.
  - Kill signature: exact no-op, higher selectivity/leakage, or fee tightening that damages floor slices.
- `ProfileTargetShadowNormalizer`
  - Layer mutation: layer 1/2 upstream observation normalization.
  - Interface boundary: normalize stress/demand before volatility, hazard, and divergence memory; do not touch downstream spread/protection/opportunity formulas directly.
  - Forbidden consumers: no direct shared spread change, burst admission, calm/refill/recapture, inventory, or layer 5/6 branch.
  - Expected movement: small mean-edge lift with lower leakage/selectivity and stronger floors.
  - Kill signature: disguised coefficient retune, over-open fee compression, exact replay, or floor damage.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round17/`
- Families explored:
  - `information_liquidity_split_bus.sol`
  - `profile_target_shadow_normalizer.sol`
  - `information_liquidity_split_bus_guarded.sol`
  - `information_liquidity_split_bus_hard_guard.sol`

### Probe Results

- Initial split bus: `InformationLiquiditySplitBus`
  - Mean edge: `486.0287876044385`
  - Delta vs incumbent baseline: `+0.10501690076665682`
  - Key profile: `arb_loss_to_retail_gain=0.09967462852137352`, `quote_selectivity_ratio=21.42303336482283`, `time_weighted_mean_fee=0.004652685118114123`
  - Floor slices: `low_decile_mean_edge=370.7685769959452`, `low_retail_mean_edge=416.03912773002963`, `low_volatility_mean_edge=463.5197274197248`
  - Outcome: small positive with floor lifts, but leakage/selectivity worsened slightly; not clean enough for retained spend.
- Shadow normalizer: `ProfileTargetShadowNormalizer`
  - Mean edge: `484.7409267266299`
  - Delta vs incumbent baseline: `-1.182843977041955`
  - Key profile: `arb_loss_to_retail_gain=0.10813918335368056`, `quote_selectivity_ratio=24.194507609475085`, `time_weighted_mean_fee=0.004469575702847986`
  - Floor slices: `low_decile_mean_edge=371.2570601888731`, `low_retail_mean_edge=415.2096655319046`, `low_volatility_mean_edge=461.73429358938523`
  - Outcome: over-open failure; lower fees and higher selectivity/leakage overwhelmed the low-decile lift.
- Guarded split bus: `InformationLiquiditySplitBusGuarded`
  - Mean edge: `486.1466492386749`
  - Delta vs incumbent baseline: `+0.2228785350030762`
  - Key profile: `arb_loss_to_retail_gain=0.09726101087767576`, `quote_selectivity_ratio=20.588897072500785`, `time_weighted_mean_fee=0.004723954398100362`
  - Floor slices: `low_decile_mean_edge=370.8088591225893`, `low_retail_mean_edge=416.2057608240779`, `low_volatility_mean_edge=463.5837490988499`
  - Outcome: clean positive, improved leakage/selectivity and floors, just below prior best raw.
- Hard-guarded split bus: `InformationLiquiditySplitBusHardGuard`
  - Mean edge: `486.22309877393417`
  - Delta vs incumbent baseline: `+0.29932807026233377`
  - Key profile: `arb_loss_to_retail_gain=0.09514752255676812`, `quote_selectivity_ratio=19.878976998553334`, `time_weighted_mean_fee=0.004786338983323556`
  - Floor slices: `low_decile_mean_edge=370.8371981784271`, `low_retail_mean_edge=416.23703934621955`, `low_volatility_mean_edge=463.53060343190987`
  - Outcome: best Round 17 scratch and structurally distinct enough for one retained screen spend.

### Retained Eval

- Retained eval: `screen_0003`
- Label: `information-liquidity-split-bus-hard-guard`
- Status: `discard`
- Mean edge: `486.22309877393417`
- Delta vs incumbent: `+0.29932807026233377`
- Promotion margin: `20.593316088696493`
- Rationale: `delta 0.299328 did not clear promotion margin 20.593316`
- Current incumbent remains `screen_0001`.

## Round 18: Adverse-Selection Component Tests Without Layer 5/6 Drift

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0003` / `information-liquidity-split-bus-hard-guard` at `486.22309877393417`.
- Breakout target: `490`.
- Round 17 established the information/liquidity split bus as the strongest upstream anchor, but the retained spend was still far below the promotion margin.

### Entropy Constraints

- Do not inspect or use oracle/reference implementation details.
- Do not use OOB, route/gap hazard, flow ownership, inventory overlay, passive recapture, quiet refill, burst admission, or scalar hazard-damper motifs.
- Include multiple topology contracts, not only split-bus coefficient variants.
- Keep all source work scratch-only unless a candidate produces a durable, structurally attributable improvement over `screen_0003`.
- Use public microstructure cues only as topology inspiration: adverse-selection and order-processing spread components, flow toxicity, and liquidity-demand decomposition.

### Accepted Probe Contracts

- `VolumeSynchronizedToxicityGate`
  - Layer mutation: layer 1/3 timing gate for flow-toxicity evidence.
  - Interface boundary: add a bounded toxicity clock into side hazard and directional flow risk only; no calm, recentering, refill, inventory, or opportunity changes.
  - Expected movement: lower leakage/selectivity while keeping fee and floor bands near `screen_0003`.
  - Kill signature: low-decile damage or no improvement over the split-bus anchor.
- `SpreadComponentAllocator`
  - Layer mutation: layer 4 shared spread decomposition.
  - Interface boundary: separate order-processing carry from adverse-selection side protection; no layer 5/6 ownership changes.
  - Expected movement: retain benign liquidity capture while improving leakage band.
  - Kill signature: broad fee-band retune, leakage/selectivity regression, or floor damage.
- `SplitBusAdverseSelectionComponent`
  - Layer mutation: layer 1/3 split-bus extension into side protection.
  - Interface boundary: keep the Round 17 information/liquidity split and add one adverse-selection component; forbidden consumers remain calm, recentering, refill, inventory, passive recapture, and layer 5/6 opportunity.
  - Expected movement: preserve Round 17 leakage/selectivity gains and recover floor slices.
  - Kill signature: same-family coefficient polish with only sub-`0.1` gain or `ProfileTargetShadowNormalizer`-style fee compression.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round18/`
- Families explored:
  - `volume_synchronized_toxicity_gate.sol`
  - `spread_component_allocator.sol`
  - `split_bus_adverse_selection_component.sol`
  - bounded split-bus refinements:
    - `split_bus_adverse_selection_soft.sol`
    - `split_bus_adverse_selection_side_only.sol`
    - `split_bus_adverse_selection_guarded.sol`

### Probe Results

- `VolumeSynchronizedToxicityGate`
  - Mean edge: `486.05598898447647`
  - Delta vs incumbent baseline: `+0.13221828080463638`
  - Delta vs retained best raw: `-0.1671097894576974`
  - Key profile: `arb_loss_to_retail_gain=0.09620320905591112`, `quote_selectivity_ratio=20.277292374747734`, `time_weighted_mean_fee=0.00474438141335465`
  - Floor slices: `low_decile_mean_edge=370.46158661085695`, `low_retail_mean_edge=416.0538529949686`, `low_volatility_mean_edge=463.6095589263268`
  - Outcome: positive vs incumbent but below the split-bus anchor; toxicity timing helped leakage but damaged low-decile enough to reject.
- `SpreadComponentAllocator`
  - Mean edge: `485.8864740258215`
  - Delta vs incumbent baseline: `-0.037296677850349624`
  - Delta vs retained best raw: `-0.3366247481126834`
  - Key profile: `arb_loss_to_retail_gain=0.09964950550641323`, `quote_selectivity_ratio=21.37617909288607`, `time_weighted_mean_fee=0.004661708019632765`
  - Floor slices: `low_decile_mean_edge=370.63154893732275`, `low_retail_mean_edge=415.8779861874194`, `low_volatility_mean_edge=463.27279522517915`
  - Outcome: rejected; layer-4 component decomposition replayed near-incumbent fee behavior and lost the Round 17 leakage/selectivity gains.
- `SplitBusAdverseSelectionComponent`
  - Mean edge: `486.240433365787`
  - Delta vs incumbent baseline: `+0.3166626621151636`
  - Delta vs retained best raw: `+0.017334591852829817`
  - Key profile: `arb_loss_to_retail_gain=0.09508474128742647`, `quote_selectivity_ratio=19.858716540176143`, `time_weighted_mean_fee=0.004788060753828711`
  - Floor slices: `low_decile_mean_edge=370.685494315755`, `low_retail_mean_edge=416.2154661162454`, `low_volatility_mean_edge=463.58996694908564`
  - Outcome: tiny same-family improvement; useful as a diagnostic but not enough for canonical spend.
- `SplitBusAdverseSelectionSoft`
  - Mean edge: `486.24083020411507`
  - Delta vs retained best raw: `+0.017731430180901953`
  - Key profile: `arb_loss_to_retail_gain=0.09507159374603591`, `quote_selectivity_ratio=19.859979187465047`, `time_weighted_mean_fee=0.004787094329184489`
  - Floor slices: `low_decile_mean_edge=370.83544929473703`, `low_retail_mean_edge=416.25502499933793`, `low_volatility_mean_edge=463.5542754121674`
  - Outcome: confirms the component is not a one-off, but still same-family and sub-`0.1`.
- `SplitBusAdverseSelectionSideOnly`
  - Mean edge: `486.24338970859253`
  - Delta vs incumbent baseline: `+0.31961900492069617`
  - Delta vs retained best raw: `+0.020290934658362403`
  - Key profile: `arb_loss_to_retail_gain=0.09508131824491939`, `quote_selectivity_ratio=19.862856393522243`, `time_weighted_mean_fee=0.0047868904834819075`
  - Floor slices: `low_decile_mean_edge=370.88667734848525`, `low_retail_mean_edge=416.2635825527519`, `low_volatility_mean_edge=463.54347683051657`
  - Outcome: best Round 18 scratch; preserves the split-bus leakage/selectivity band and improves low-decile/low-retail, but the gain is too small and too local to justify a retained eval under the current entropy constraint.
- `SplitBusAdverseSelectionGuarded`
  - Mean edge: `486.2404278271643`
  - Delta vs retained best raw: `+0.01732905323012801`
  - Outcome: no meaningful improvement over the unguarded component; calm gating was effectively redundant.

### Decision

- No Round 18 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0003`
- Keep `SplitBusAdverseSelectionSideOnly` as a scratch-only diagnostic anchor, not an official retained best raw.

### Updated Entropy Discipline

- The split-bus family is productive but close to local polish. Do not spend the next round only on split-bus coefficient changes.
- If the split-bus side-only component is revisited, pair it with exactly one structurally different primary topology and keep it as the secondary adjunct.
- `SpreadComponentAllocator` suggests layer-4 decomposition without a stronger upstream primary signal is not enough.
- `VolumeSynchronizedToxicityGate` is an outsider topology worth remembering, but the current activation damages low-decile; do not repeat it without a different floor-preserving estimator selection.
- Round 19 should start from at least two non-split-bus primary contracts, preferably a regime-conditioned estimator selector and an exogenous-profile guardrail that stays upstream/mid-scaffold.

## Round 19: Regime-Conditioned Estimator Selection

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0003` / `information-liquidity-split-bus-hard-guard` at `486.22309877393417`.
- Breakout target: `490`.
- Round 18 kept the split-bus adverse-selection side component scratch-only because it was same-family and only `+0.020290934658362403` over retained best raw.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round19/`
- Families explored:
  - `regime_conditioned_estimator_selector.sol`
  - `floor_preserving_toxicity_clock.sol`
  - `profile_relative_fee_guard.sol`

### Probe Results

- `RegimeConditionedEstimatorSelector`
  - Mean edge: `486.7742926627275`
  - Delta vs incumbent baseline: `+0.8505219590556408`
  - Delta vs prior retained best raw: `+0.5511938887933283`
  - Key profile: `arb_loss_to_retail_gain=0.0927757621971137`, `quote_selectivity_ratio=19.154020954118753`, `time_weighted_mean_fee=0.004843670288309036`
  - Floor slices: `low_decile_mean_edge=371.4047024415447`, `low_retail_mean_edge=416.76910064194493`, `low_volatility_mean_edge=463.93316278416495`
  - Outcome: strongest non-split-bus scratch of the late run; improved leakage/selectivity and all tracked floors enough to justify a retained spend.
- `FloorPreservingToxicityClock`
  - Mean edge: `486.1236498651966`
  - Key profile: `arb_loss_to_retail_gain=0.09742718544754407`, `quote_selectivity_ratio=20.67799256784341`, `time_weighted_mean_fee=0.004711636544402972`
  - Floor slices: `low_decile_mean_edge=370.74821500366653`, `low_retail_mean_edge=416.02007200010536`, `low_volatility_mean_edge=463.478670978248`
  - Outcome: positive vs incumbent but below the split-bus anchor and weaker than the regime selector.
- `ProfileRelativeFeeGuard`
  - Mean edge: `485.9781036450237`
  - Key profile: `arb_loss_to_retail_gain=0.09580794588896566`, `quote_selectivity_ratio=20.071692814606333`, `time_weighted_mean_fee=0.004773286776252645`
  - Floor slices: `low_decile_mean_edge=370.7627619110177`, `low_retail_mean_edge=416.1102924298279`, `low_volatility_mean_edge=463.4429299694617`
  - Outcome: near-frontier but too small; retained only as a diagnostic guardrail.

### Retained Eval

- Retained eval: `screen_0004`
- Label: `regime-conditioned-estimator-selector`
- Status: `discard`
- Mean edge: `486.7742926627275`
- Delta vs incumbent: `+0.8505219590556408`
- Promotion margin: `20.59660878784334`
- Rationale: `delta 0.850522 did not clear promotion margin 20.596609`
- Current incumbent remains `screen_0001`.

## Round 20: Stronger Floor Guard Around The Regime Selector

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0004` / `regime-conditioned-estimator-selector` at `486.7742926627275`.
- Breakout target: `490`.
- Entropy constraint: allow one regime-selector follow-up only if paired against collapse tests and not turned into broad fee release or burst-bridge repair.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round20/`
- Families explored:
  - `regime_selector_stronger_floor.sol`
  - `regime_selector_burst_pivot_bridge.sol`
  - `regime_selector_mild_fee_release.sol`

### Probe Results

- `RegimeSelectorStrongerFloor`
  - Mean edge: `487.01236396243195`
  - Delta vs incumbent baseline: `+1.0885932587601133`
  - Delta vs retained best raw: `+0.23807129970444764`
  - Key profile: `arb_loss_to_retail_gain=0.09201952529170741`, `quote_selectivity_ratio=18.915717013826818`, `time_weighted_mean_fee=0.004864712515229738`
  - Floor slices: `low_decile_mean_edge=371.5875792256349`, `low_retail_mean_edge=416.87678274382506`, `low_volatility_mean_edge=464.14737531113127`
  - Outcome: improved mean edge, leakage/selectivity, and all tracked floors over `screen_0004`; strong enough for one retained spend despite staying within the regime-selector family.
- `RegimeSelectorBurstPivotBridge`
  - Mean edge: `474.3540575417355`
  - Key profile: `arb_loss_to_retail_gain=0.11598602989897484`, `quote_selectivity_ratio=24.55455594837189`, `time_weighted_mean_fee=0.004723605270763017`
  - Floor slices: `low_decile_mean_edge=304.475361612637`, `low_retail_mean_edge=399.1252729739719`, `low_volatility_mean_edge=464.2625093867264`
  - Outcome: rejected; burst bridge collapsed low-decile and low-retail floors.
- `RegimeSelectorMildFeeRelease`
  - Mean edge: `456.29146432776923`
  - Key profile: `arb_loss_to_retail_gain=0.15342245720426423`, `quote_selectivity_ratio=34.502647498201675`, `time_weighted_mean_fee=0.004446686510426796`
  - Floor slices: `low_decile_mean_edge=263.2819728995887`, `low_retail_mean_edge=398.91702632222564`, `low_volatility_mean_edge=440.36047340124884`
  - Outcome: rejected; broad fee release replayed the over-open leak basin.

### Retained Eval

- Retained eval: `screen_0005`
- Label: `regime-selector-stronger-floor`
- Status: `discard`
- Mean edge: `487.01236396243195`
- Delta vs incumbent: `+1.0885932587601133`
- Promotion margin: `20.617091291129682`
- Rationale: `delta 1.088593 did not clear promotion margin 20.617091`
- Current incumbent remains `screen_0001`.

### Updated Entropy Discipline

- Treat `screen_0005` as the current best raw anchor and measurement baseline, not as permission for a Round 21 coefficient-polish batch.
- Do not spend Round 21 on `regime_selector_stronger_floor_2`, mild fee release, burst-pivot bridge repair, or split-bus side-only coefficient variants.
- The next batch must include at least two primary candidates outside split-bus/regime-selector vocabulary and can include at most one layer 6 safe-side service slot.
