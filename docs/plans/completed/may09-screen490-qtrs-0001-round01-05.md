# may09-screen490-qtrs-0001 rounds 01-05

Run index: [may09-screen490-qtrs-0001.md](may09-screen490-qtrs-0001.md)

## Opening State

- Active retained lane: `may09-screen490-qtrs-0001`.
- Retained seed: `screen_0001` / `seed-from-apr21-screen0007` at `487.54341156295743`.
- Breakout target: `490`.
- Source seed: Apr21 `screen_0007` / `QuantileTailRiskSketch`.
- Prior parked lane: [may08-screen490-0001.md](may08-screen490-0001.md).

## Seed Decision

The May08 WCEF-seeded lane produced two scratch rounds and a third-round entropy blocker without a retained eval. This lane deliberately changes seed frame to the Apr21 tail-state anchor instead of continuing WCEF-local sensor, consumer, spread-atom, divergence-write, or direct-fee surfaces.

## Carry-Forward Constraints

- Treat `QuantileTailRiskSketch` as the incumbent seed, not as permission for local tail-bucket threshold or consumer tuning.
- Use `docs/combination_anchor_map.md` for durable saturated-basin and anchor lessons from Apr21 and May08.
- Keep retained writes serialized through `hill-climb eval`; use `hill-climb probe` for scratch scouting.
- Do not mutate Apr21 or May08 retained ledgers while continuing this lane.
- Enforce proposer -> critic ordering and require at least four genuinely distinct critic-accepted designs before worker/source edits.

## Round 1: Tail-State Seed-Frame Batch

### Starting State

- Active retained lane: `may09-screen490-qtrs-0001`.
- Retained incumbent: `screen_0001` / `seed-from-apr21-screen0007` at `487.54341156295743`.
- Breakout target: `490`.
- Gap to target: `2.456588437042572`.
- The checked-out `contracts/src/StarterStrategy.sol` was restored from the retained May09 seed and revalidated as `QuantileTailRiskSketch`.

### Subagent Workflow

- Topology proposer produced seven QTRS-frame candidates.
- Saturation/entropy critic accepted four and rejected three:
  - Accepted `TailCutImmunityInvariant`, `ToxicSideCapFloorDecoupler`, `ShortLongTailConsumerSplit`, and `CounterflowProofBeforeRelief`.
  - Rejected `SparseTrafficFloorCertificate` as classifier-local floor routing into existing consumers.
  - Rejected `CalmSurplusEscrowBeforeRebate` as same-spine tail reserve / allocation-release replay.
  - Rejected `TailConditionedDecayBrake` as scalar state-write / EMA memory polish.
- Enforced entropy constraints:
  - at least four critic-accepted designs before source work
  - scratch-only worker scope under this run's `round1/` directory
  - no retained-ledger edits by workers
  - no tail threshold / cap coefficient tuning, WCEF-local sensor floors, May08 consumer rewires, direct fee/base spread edits, standalone refill/recapture/opportunity cuts, or layer5/6 diagnostics without upstream tail-ownership change

### Probe Sources

- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round1/tail_cut_immunity_invariant/tail_cut_immunity_invariant.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round1/toxic_side_cap_floor_decoupler/toxic_side_cap_floor_decoupler.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round1/short_long_tail_consumer_split/short_long_tail_consumer_split.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round1/counterflow_proof_before_relief/counterflow_proof_before_relief.sol`

### Probe Results

- `TailCutImmunityInvariant`
  - Mean edge: `485.909097954837`
  - Delta vs seed: `-1.634313608120408`
  - Key profile: `arb_loss_to_retail_gain=0.09159259863007892`, `quote_selectivity_ratio=18.587379299513664`, `time_weighted_mean_fee=0.004927676847508859`
  - Floor slices: `low_decile_mean_edge=370.93476618437495`, `low_retail_mean_edge=416.20825779189204`, `low_volatility_mean_edge=463.21638660857735`
  - Outcome: killed as tail-reserve over-tightening / floor loss.
- `ToxicSideCapFloorDecoupler`
  - Mean edge: `486.79862210515984`
  - Delta vs seed: `-0.7447894577975944`
  - Key profile: `arb_loss_to_retail_gain=0.08004754697392819`, `quote_selectivity_ratio=15.004655660996388`, `time_weighted_mean_fee=0.0053348473155572975`
  - Floor slices: `low_decile_mean_edge=370.1511765886604`, `low_retail_mean_edge=416.22213204667895`, `low_volatility_mean_edge=464.0278073689808`
  - Outcome: killed as asymmetric cap split overcharge; leakage/selectivity improved only by losing mean and floors.
- `ShortLongTailConsumerSplit`
  - Mean edge: `487.46493645383447`
  - Delta vs seed: `-0.0784751091229623`
  - Key profile: `arb_loss_to_retail_gain=0.09236059295020521`, `quote_selectivity_ratio=19.229244918526962`, `time_weighted_mean_fee=0.004803131549966259`
  - Floor slices: `low_decile_mean_edge=372.19232407975034`, `low_retail_mean_edge=417.5966600284601`, `low_volatility_mean_edge=464.7741877813381`
  - Outcome: closest miss, killed as sub-seed temporal consumer split with worse leakage/selectivity and lower retail / volatility floors.
- `CounterflowProofBeforeRelief`
  - Mean edge: `485.5669817118045`
  - Delta vs seed: `-1.9764298511529432`
  - Key profile: `arb_loss_to_retail_gain=0.09194440939904165`, `quote_selectivity_ratio=18.558652317592475`, `time_weighted_mean_fee=0.00495426110827476`
  - Floor slices: `low_decile_mean_edge=370.5566899502119`, `low_retail_mean_edge=415.7641080053942`, `low_volatility_mean_edge=462.9335429445255`
  - Outcome: killed as narrow relief-proof over-tightening / floor loss.

### Decision

- No Round 1 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw in the May09 lane: `screen_0001`
  - best raw mean edge: `487.54341156295743`
  - gap to breakout target: `2.456588437042572`

### Validation And Commands

- Restored retained seed: `uv run amm-match hill-climb pull-best --run-id may09-screen490-qtrs-0001 --stage screen --destination contracts/src/StarterStrategy.sol`.
- Revalidated retained seed: `uv run amm-match validate contracts/src/StarterStrategy.sol`.
- Validated all four accepted scratch sources with `uv run amm-match validate`.
- Ran each scratch probe with `uv run amm-match hill-climb probe --stage screen --json <source>` and wrote the JSON result beside the source.

### Updated Entropy Discipline

- QTRS tail-rights rewiring did not break out. Preserving tail reserves, splitting toxic-side caps, temporal tail routing, and narrow relief proofs all stayed below the QTRS seed.
- `ShortLongTailConsumerSplit` is the only near miss, but it worsened leakage/selectivity and lost low-retail / low-volatility floors, so temporal tail partitioning is not a retained anchor by itself.
- Direct tail-protection preservation under this seed tends to buy lower leakage/selectivity by over-tightening and giving back mean/floors. Next proposals should not keep rearranging tail protection, opportunity-cut reserve, side cap/floor split, long-tail calm suppression, or relief proof gates unless they introduce a different primary owner outside QTRS tail consumer rights.

## Round 2: Non-Tail-Rights Side-Risk Batch

### Starting State

- Active retained lane: `may09-screen490-qtrs-0001`.
- Retained incumbent: `screen_0001` / `seed-from-apr21-screen0007` at `487.54341156295743`.
- Best raw before the round: `screen_0001`.
- Breakout target: `490`.
- Round 1 closed with no retained eval and a new constraint: no more QTRS tail reserve, side cap/floor split, long-tail calm suppression, or relief-proof gates unless a proposal introduces a different primary owner outside tail consumer rights.

### Subagent Workflow

- Topology proposer produced six non-tail-right candidates:
  - `SignedImpactAbsorptionBus`
  - `SlippageElasticityResponseOwner`
  - `FlowShareEntropyRiskGate`
  - `PrePostInvariantDisplacementCodec`
  - `ProtectionMassConservationRouter`
  - `AdverseBenignOrthogonalBasis`
- Saturation/entropy critic accepted four and rejected two:
  - Accepted `SlippageElasticityResponseOwner`, `FlowShareEntropyRiskGate`, `ProtectionMassConservationRouter`, and `AdverseBenignOrthogonalBasis`.
  - Rejected `SignedImpactAbsorptionBus` as same-spine split-bus / flow-ownership polish / state-write scalar replay.
  - Rejected `PrePostInvariantDisplacementCodec` as upstream geometry-codec / invariant-residual replay.
- Enforced entropy constraints:
  - at least four critic-accepted designs before source work
  - scratch-only worker scope under this run's `round2/` directory
  - no retained-ledger edits by workers
  - no QTRS tail consumer-right replay, WCEF / May08 replay, state-write scalar polish, direct fee/base-spread edits, or broad release deletion

### Probe Sources

- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round2/slippage_elasticity_response_owner/slippage_elasticity_response_owner.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round2/flow_share_entropy_risk_gate/flow_share_entropy_risk_gate.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round2/protection_mass_conservation_router/protection_mass_conservation_router.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round2/adverse_benign_orthogonal_basis/adverse_benign_orthogonal_basis.sol`

### Probe Results

- `SlippageElasticityResponseOwner`
  - Mean edge: `487.41763470846263`
  - Delta vs seed: `-0.12577685449480214`
  - Key profile: `arb_loss_to_retail_gain=0.09207197850022492`, `quote_selectivity_ratio=19.10503930254222`, `time_weighted_mean_fee=0.004819250933860854`
  - Floor slices: `low_decile_mean_edge=372.330681247566`, `low_retail_mean_edge=417.6451950680837`, `low_volatility_mean_edge=464.6081033093969`
  - Outcome: killed as sub-seed response-elasticity side-risk routing; low-volatility floor fell without mean lift.
- `FlowShareEntropyRiskGate`
  - Scratch mean edge: `487.57113729193804`
  - Delta vs seed: `+0.027725728980612985`
  - Key profile: `arb_loss_to_retail_gain=0.09221653706675405`, `quote_selectivity_ratio=19.17922671380272`, `time_weighted_mean_fee=0.004808146774780473`
  - Floor slices: `low_decile_mean_edge=372.1784815453956`, `low_retail_mean_edge=417.63922550936076`, `low_volatility_mean_edge=464.85416129888546`
  - Outcome: spent one retained eval because scratch beat seed; retained as best raw `screen_0002` but discarded as incumbent because `delta 0.027726` did not clear promotion margin `20.619543`.
- `ProtectionMassConservationRouter`
  - Mean edge: `464.47993348590603`
  - Delta vs seed: `-23.0634780770514`
  - Key profile: `arb_loss_to_retail_gain=0.1586088163909226`, `quote_selectivity_ratio=38.55054967993323`, `time_weighted_mean_fee=0.004114307518512076`
  - Floor slices: `low_decile_mean_edge=358.208319423308`, `low_retail_mean_edge=397.603056276932`, `low_volatility_mean_edge=443.69351916864247`
  - Outcome: killed as allocation-release hidden release with sharp leakage/selectivity worsening and floor collapse.
- `AdverseBenignOrthogonalBasis`
  - Mean edge: `473.2971609475231`
  - Delta vs seed: `-14.246250615434349`
  - Key profile: `arb_loss_to_retail_gain=0.12020725228389541`, `quote_selectivity_ratio=26.025770728794942`, `time_weighted_mean_fee=0.00461877780821676`
  - Floor slices: `low_decile_mean_edge=292.0014054450461`, `low_retail_mean_edge=399.6009839748336`, `low_volatility_mean_edge=464.8824165323589`
  - Outcome: killed as adverse/benign split-basis hidden release with low-decile and low-retail collapse.

### Decision

- One Round 2 scratch candidate earned a canonical retained eval:
  - `screen_0002` / `flow-share-entropy-risk-gate` at `487.57113729193804`
  - Status: `discard`
  - Selection rationale: `delta 0.027726 did not clear promotion margin 20.619543`
- Retained lane state after the round:
  - incumbent: `screen_0001` / `QuantileTailRiskSketch`
  - incumbent mean edge: `487.54341156295743`
  - best raw in the May09 lane: `screen_0002` / `FlowShareEntropyRiskGate`
  - best raw mean edge: `487.57113729193804`
  - best raw gap to breakout target: `2.428862708061956`

### Validation And Commands

- Validated all four accepted scratch sources with `uv run amm-match validate`.
- Ran each scratch probe with `uv run amm-match hill-climb probe --stage screen --json <source>` and wrote the JSON result beside the source.
- Spent retained eval with `uv run amm-match hill-climb eval --run-id may09-screen490-qtrs-0001 --stage screen --label flow-share-entropy-risk-gate --json artifacts/scratch_probes/may09-screen490-qtrs-0001/round2/flow_share_entropy_risk_gate/flow_share_entropy_risk_gate.sol`.
- Verified live retained state with `uv run amm-match hill-climb status --run-id may09-screen490-qtrs-0001 --json`.

### Updated Entropy Discipline

- `FlowShareEntropyRiskGate` is a legitimate best-raw signal, but the gain is tiny and comes with slightly worse leakage/selectivity plus low-decile and low-retail giveback; do not treat flow-share entropy as the new incumbent semantics.
- `ProtectionMassConservationRouter` shows fixed-mass side routing can still create allocation-release hidden release; avoid conservation-router variants unless they prove no side floor collapse.
- `AdverseBenignOrthogonalBasis` replays split-bus hidden release despite one-way benign semantics; avoid adverse/benign classifier vocabulary under this seed unless it has a new owner outside side-risk weighting.
- `SlippageElasticityResponseOwner` was a near-frontier sub-seed miss. Response elasticity alone is not enough unless the next proposal uses a different consumer than side-risk / directional-risk assembly.

## Round 3: Subagent Availability Blocker

### Starting State

- Active retained lane: `may09-screen490-qtrs-0001`.
- Official incumbent: `screen_0001` / `QuantileTailRiskSketch` at `487.54341156295743`.
- Best raw: `screen_0002` / `FlowShareEntropyRiskGate` at `487.57113729193804`, status `discard`.
- Breakout target: `490`.
- Best raw gap to breakout target: `2.428862708061956`.

### Blocker

- The coordinator attempted to start the Round 3 proposer subagent after Round 2 notes were updated.
- The subagent failed before producing a proposal due the current account usage limit.
- A lightweight retry at `2026-05-09 01:12 CEST` also failed with the same usage-limit message and platform reset time `02:21`.
- No Round 3 proposal, critic review, scratch source work, or retained eval was performed.
- Handoff integrity check: all recorded May08 Rounds 1-2 and May09 Rounds 1-2 scratch Solidity files still pass `uv run amm-match validate` from disk.

### Continuation Constraint

- Do not treat `screen_0002` as official incumbent semantics. It is a weak best-raw measurement anchor only.
- The next proposer -> critic pass must exclude:
  - Round 1 tail consumer-right rewires: tail reserve / cut immunity, toxic-side cap/floor split, short/long tail calm suppression, counterflow/refill/healing proof gates
  - Round 2 non-tail side-risk surfaces: flow-share entropy polish, response-elasticity side-risk assembly, fixed-mass protection routing, adverse/benign split bases, signed-impact flow bus, and pre/post invariant geometry codec
  - May08 WCEF-local sensor floors, consumer rewires, direct fee/base spread edits, spread atoms, divergence writes, calm provenance, cut eligibility, and latent commit order
- If the next proposer cannot defend at least four genuinely distinct designs under those exclusions, record QTRS-frame saturation and switch seed/search frame instead of padding names.

### Resume Checklist

- Refresh live state with `uv run amm-match hill-climb status --run-id may09-screen490-qtrs-0001 --json` before any proposal work.
- Confirm source alignment before source work: `contracts/src/StarterStrategy.sol` intentionally matches official incumbent `screen_0001` / `QuantileTailRiskSketch` (`7fce3149b3de21ffd8894fb9593eb111219b2b99bdbc67cbe8eef1847436f28c`), not best-raw discard `screen_0002` / `FlowShareEntropyRiskGate`.
- Restart with a proposer subagent first. It must produce at least six distinct candidates or explicitly declare QTRS-frame saturation; each candidate must name base (`screen_0001` official incumbent or `screen_0002` weak best raw), primary owner, allowed consumers, forbidden consumers, expected metric movement, and kill signature.
- Run the saturation/entropy critic after proposer and before source work. If fewer than four genuinely distinct candidates survive, do not open worker edits.
- Keep any accepted worker probes scratch-only under `artifacts/scratch_probes/may09-screen490-qtrs-0001/round3/`; retained eval is reserved for candidates that beat the active run's live best raw or show a genuinely new floor-risk owner with materially better named floor slices.

### Subagent Workflow

- After the subagent reset, the Round 3 topology proposer produced six candidates:
  - `CreditStackExclusivityCompiler`
  - `AdverseDurationOccupancyBox`
  - `VolatilityAccelerationCircuit`
  - `BenignMicrotradeSafeBand`
  - `IndependentStressConjunctionGate`
  - `ProtectionContinuityDebtLimiter`
- Saturation/entropy critic accepted four and rejected two:
  - Accepted `CreditStackExclusivityCompiler`, `AdverseDurationOccupancyBox`, `VolatilityAccelerationCircuit`, and `BenignMicrotradeSafeBand`.
  - Rejected `IndependentStressConjunctionGate` as classifier-local quorum / floor-drag risk.
  - Rejected `ProtectionContinuityDebtLimiter` as flow-share entropy polish / weak-anchor stacking from discarded `screen_0002`.
- Enforced entropy constraints:
  - at least four critic-accepted designs before source work
  - scratch-only worker scope under this run's `round3/` directory
  - no Round 1 tail consumer-right replay, Round 2 side-risk replay, May08 WCEF replay, direct fee/base-spread edits, broad release deletion, upstream geometry-codec retreads, or weak-anchor stacking

### Probe Sources

- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round3/benign_microtrade_safe_band/benign_microtrade_safe_band.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round3/adverse_duration_occupancy_box/adverse_duration_occupancy_box.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round3/volatility_acceleration_circuit/volatility_acceleration_circuit.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round3/credit_stack_exclusivity_compiler/credit_stack_exclusivity_compiler.sol`

### Probe Results

- `BenignMicrotradeSafeBand`
  - Mean edge: `487.5431205373723`
  - Delta vs incumbent: `-0.0002910255851134025`
  - Delta vs prior best raw `screen_0002`: `-0.028016754565726387`
  - Key profile: `arb_loss_to_retail_gain=0.09217121410457214`, `quote_selectivity_ratio=19.158458040699724`, `time_weighted_mean_fee=0.0048109933434499815`
  - Floor slices: `low_decile_mean_edge=372.18921614578545`, `low_retail_mean_edge=417.66009216093516`, `low_volatility_mean_edge=464.8243841482259`
  - Outcome: killed as phenotype-near no-op; it improved tiny floor slices but missed both incumbent and best raw.
- `AdverseDurationOccupancyBox`
  - Mean edge: `487.61930920009956`
  - Delta vs incumbent: `+0.07589763714213404`
  - Delta vs prior best raw `screen_0002`: `+0.04817190816152106`
  - Key profile: `arb_loss_to_retail_gain=0.0909716351461104`, `quote_selectivity_ratio=18.753342747078545`, `time_weighted_mean_fee=0.004850955713497118`
  - Floor slices: `low_decile_mean_edge=372.0474894765317`, `low_retail_mean_edge=417.5942291970161`, `low_volatility_mean_edge=464.6545750230551`
  - Outcome: killed as duration-occupancy protection with low-decile, low-retail, and low-volatility giveback despite mean / leakage improvement.
- `VolatilityAccelerationCircuit`
  - Scratch mean edge: `487.7145544914556`
  - Delta vs incumbent: `+0.17114292849817048`
  - Delta vs prior best raw `screen_0002`: `+0.1434171995175575`
  - Key profile: `arb_loss_to_retail_gain=0.08114499362159378`, `quote_selectivity_ratio=15.54310381792704`, `time_weighted_mean_fee=0.00522064283762958`
  - Floor slices: `low_decile_mean_edge=371.5392105870849`, `low_retail_mean_edge=417.6224702896166`, `low_volatility_mean_edge=465.03059076963365`
  - Outcome: spent one retained eval because scratch beat live best raw; retained as best raw `screen_0003` but discarded as incumbent because `delta 0.171143` did not clear promotion margin `20.741922`. Treat as risky overprotection: leakage/selectivity improved, but fee rose above the overcharge warning band and low-decile / low-retail fell.
- `CreditStackExclusivityCompiler`
  - Mean edge: `485.6148143490484`
  - Delta vs incumbent: `-1.928597213909029`
  - Delta vs prior best raw `screen_0002`: `-1.956322942889642`
  - Key profile: `arb_loss_to_retail_gain=0.0921161210169009`, `quote_selectivity_ratio=18.656110542821846`, `time_weighted_mean_fee=0.0049375844340900765`
  - Floor slices: `low_decile_mean_edge=370.570233499132`, `low_retail_mean_edge=415.9103899139513`, `low_volatility_mean_edge=462.90314735669193`
  - Outcome: killed as relief-removal overcharge / floor loss.

### Decision

- One Round 3 scratch candidate earned a canonical retained eval:
  - `screen_0003` / `volatility-acceleration-circuit` at `487.7145544914556`
  - Status: `discard`
  - Selection rationale: `delta 0.171143 did not clear promotion margin 20.741922`
- Retained lane state after the round:
  - incumbent: `screen_0001` / `QuantileTailRiskSketch`
  - incumbent mean edge: `487.54341156295743`
  - best raw in the May09 lane: `screen_0003` / `VolatilityAccelerationCircuit`
  - best raw mean edge: `487.7145544914556`
  - best raw gap to breakout target: `2.2854455085443895`

### Validation And Commands

- Validated all four accepted scratch sources with `uv run amm-match validate`.
- Ran each scratch probe with `uv run amm-match hill-climb probe --stage screen --json <source>` and wrote the JSON result beside the source.
- Spent retained eval with `uv run amm-match hill-climb eval --run-id may09-screen490-qtrs-0001 --stage screen --label volatility-acceleration-circuit --json artifacts/scratch_probes/may09-screen490-qtrs-0001/round3/volatility_acceleration_circuit/volatility_acceleration_circuit.sol`.
- Verified live retained state with `uv run amm-match hill-climb status --run-id may09-screen490-qtrs-0001 --json`.

### Updated Entropy Discipline

- `VolatilityAccelerationCircuit` is the new best raw measurement anchor, but it is not official incumbent semantics. Its mean gain is bought with higher fee and low-decile / low-retail giveback.
- Do not locally polish acceleration pulse coefficients unless the next proposal names a different owner that repairs the low-decile / low-retail loss without broad fee overcharge.
- `AdverseDurationOccupancyBox` is a weaker version of the same protection-vs-floor tradeoff; avoid continuation-duration occupancy unless a separate floor-preservation owner is present.
- `BenignMicrotradeSafeBand` was a near no-op, and `CreditStackExclusivityCompiler` over-tightened into floor loss. Do not continue microtrade cap or credit-stack exclusivity as primary owners under this seed.

## Round 4: Vector-Order Repair Batch

### Starting State

- Active retained lane: `may09-screen490-qtrs-0001`.
- Official incumbent: `screen_0001` / `QuantileTailRiskSketch` at `487.54341156295743`.
- Best raw before the round: `screen_0003` / `VolatilityAccelerationCircuit` at `487.7145544914556`, status `discard`.
- Breakout target: `490`.
- Best raw gap to breakout target: `2.2854455085443895`.

### Subagent Workflow

- Round 4 proposer first produced six candidates: `IncrementalProtectionDutyCycleLedger`, `SubadditiveProtectionReasonCompiler`, `FalsePositiveProtectionScorecard`, `CurveTangentServiceEnvelope`, `TypedShockCausalityMux`, and `ShadowPriceConsensusBand`.
- Saturation/entropy critic accepted only two, so worker edits remained blocked:
  - Accepted `FalsePositiveProtectionScorecard` and `ShadowPriceConsensusBand`.
  - Rejected `IncrementalProtectionDutyCycleLedger` as acceleration duty-cycle / protection-continuity replay.
  - Rejected `SubadditiveProtectionReasonCompiler` as final protection aggregation / credit-stack replay.
  - Rejected `CurveTangentServiceEnvelope` as invariant / geometry-codec and service-envelope saturation.
  - Rejected `TypedShockCausalityMux` as stress-conjunction / causal-label hazard-codec replay.
- Replacement proposer produced six more candidates. Critic accepted two and rejected four, bringing the combined batch to the four-design floor:
  - Accepted `MajorizationRiskVectorFilter` and `RiskMemoryAntiWindupIntegrator`.
  - Rejected `BoundedInfluenceHazardEstimator` as upstream estimator / geometry-codec replay too close to shadow consensus.
  - Rejected `CensoredCalmWriteBarrier` as calm-memory provenance / latent-write barrier replay.
  - Rejected `ProtectedWidthDrawdownObserver` as false-positive / floor-drawdown diagnostic replay and weak stacking with the vector filter.
  - Rejected `BidAskMirrorStabilityGate` as the same bid/ask asymmetry family as the accepted vector-order slot.
- Enforced entropy constraints:
  - no worker edits until at least four critic-accepted designs existed
  - scratch-only worker scope under this run's `round4/` directory
  - no direct fee/base-spread edits, broad release deletion, tail consumer-right replay, flow-share polish, acceleration pulse/cap polish, final protection compiler, curve/service geometry, typed shock co-occurrence, WCEF/event-feasibility residual polish, or weak-anchor stacking

### Probe Sources

- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round4/false_positive_protection_scorecard/false_positive_protection_scorecard.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round4/shadow_price_consensus_band/shadow_price_consensus_band.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round4/majorization_risk_vector_filter/majorization_risk_vector_filter.sol`
- `artifacts/scratch_probes/may09-screen490-qtrs-0001/round4/risk_memory_anti_windup_integrator/risk_memory_anti_windup_integrator.sol`

### Probe Results

- `FalsePositiveProtectionScorecard`
  - Mean edge: `408.7695587866578`
  - Delta vs incumbent: `-78.77385277629963`
  - Delta vs prior best raw `screen_0003`: `-78.94499570479781`
  - Key profile: `arb_loss_to_retail_gain=0.2447693605510286`, `quote_selectivity_ratio=61.70606081121308`, `time_weighted_mean_fee=0.003966698851509732`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=362.5109003231721`, `low_volatility_mean_edge=416.4994971210322`
  - Outcome: killed as false-positive throttle hidden release with severe leakage/selectivity and floor collapse.
- `ShadowPriceConsensusBand`
  - Mean edge: `400.07972436134656`
  - Delta vs incumbent: `-87.46368720161087`
  - Delta vs prior best raw `screen_0003`: `-87.63483013010905`
  - Key profile: `arb_loss_to_retail_gain=0.2153944704770445`, `quote_selectivity_ratio=33.820275621550344`, `time_weighted_mean_fee=0.006368797016538645`
  - Floor slices: `low_decile_mean_edge=223.99627885221182`, `low_retail_mean_edge=358.2949995011161`, `low_volatility_mean_edge=398.5738181797556`
  - Outcome: killed as shadow-consensus evidence overcharge / floor collapse.
- `MajorizationRiskVectorFilter`
  - Scratch mean edge: `487.7232131981818`
  - Delta vs incumbent: `+0.17980163522435078`
  - Delta vs prior best raw `screen_0003`: `+0.0086587067261803`
  - Key profile: `arb_loss_to_retail_gain=0.08115829800064478`, `quote_selectivity_ratio=15.546980709243456`, `time_weighted_mean_fee=0.005220196739061503`
  - Floor slices: `low_decile_mean_edge=371.5332084297802`, `low_retail_mean_edge=417.61900522444324`, `low_volatility_mean_edge=465.0424150356596`
  - Outcome: spent one retained eval because scratch beat live best raw, but it failed the floor-repair kill signature and remains an overprotection measurement anchor only.
- `RiskMemoryAntiWindupIntegrator`
  - Mean edge: `487.7145019706798`
  - Delta vs incumbent: `+0.17109040772236498`
  - Delta vs prior best raw `screen_0003`: `-0.0000525207757978`
  - Key profile: `arb_loss_to_retail_gain=0.08114513684830746`, `quote_selectivity_ratio=15.543138875365498`, `time_weighted_mean_fee=0.005220640277294011`
  - Floor slices: `low_decile_mean_edge=371.5392054188246`, `low_retail_mean_edge=417.6224661965503`, `low_volatility_mean_edge=465.03058380421413`
  - Outcome: killed as phenotype-identical anti-windup near-no-op; it did not repair `screen_0003` floors or beat live best raw.

### Decision

- One Round 4 scratch candidate earned a canonical retained eval:
  - `screen_0004` / `majorization-risk-vector-filter` at `487.7232131981818`
  - Status: `discard`
  - Selection rationale: `delta 0.179802 did not clear promotion margin 20.742483`
- Retained lane state after the round:
  - incumbent: `screen_0001` / `QuantileTailRiskSketch`
  - incumbent mean edge: `487.54341156295743`
  - best raw in the May09 lane: `screen_0004` / `MajorizationRiskVectorFilter`
  - best raw mean edge: `487.7232131981818`
  - best raw gap to breakout target: `2.2767868018182185`

### Validation And Commands

- Validated all four accepted scratch sources with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match validate`.
- Ran each scratch probe with `rtk proxy sh -c 'UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb probe --stage screen --json <source> > <result.json>'`.
- Spent retained eval with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb eval --run-id may09-screen490-qtrs-0001 --stage screen --label majorization-risk-vector-filter --json artifacts/scratch_probes/may09-screen490-qtrs-0001/round4/majorization_risk_vector_filter/majorization_risk_vector_filter.sol`.
- Verified live retained state with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb status --run-id may09-screen490-qtrs-0001 --json`.

### Updated Entropy Discipline

- `MajorizationRiskVectorFilter` is the new best raw measurement anchor, but it is not official incumbent semantics. It barely improves `screen_0003` mean and still carries the same high-fee, low-decile, and low-retail giveback.
- Do not locally polish bid/ask vector-order filters, side-risk dominance gates, or the `screen_0003` acceleration family unless the next proposal names a different floor-preserving owner.
- `FalsePositiveProtectionScorecard` and `ShadowPriceConsensusBand` are hard failures under this seed: delayed false-positive throttling created hidden release, while shadow consensus overcharged into broad floor collapse.
- `RiskMemoryAntiWindupIntegrator` was phenotype-identical to `screen_0003`; stale-risk memory writes alone are not a productive primary owner here.
- Round 5 must start from a fresh proposer -> critic pass against `screen_0004` best raw and should explicitly exclude false-positive scorecards, shadow consensus bands, vector-order side filters, anti-windup memory writes, and all previously rejected Round 4 families.

## Round 5: QTRS-Local Saturation Gate

### Starting State

- Active retained lane: `may09-screen490-qtrs-0001`.
- Official incumbent: `screen_0001` / `QuantileTailRiskSketch` at `487.54341156295743`.
- Best raw before the round: `screen_0004` / `MajorizationRiskVectorFilter` at `487.7232131981818`, status `discard`.
- Breakout target: `490`.
- Best raw gap to breakout target: `2.2767868018182185`.

### Proposer Result

- The Round 5 proposer declared QTRS-local saturation and did not supply a worker batch.
- The proposer could not defend six genuinely distinct candidates under the expanded exclusions without replaying prior families:
  - size / impact efficiency owners replay response-elasticity side-risk
  - alternating / counterflow proofs replay signed-impact bus or counterflow relief gates
  - hazard write passivity / backpressure replays anti-windup memory writes or censored calm barriers
  - fee-jump / high-fee envelopes become direct fee or final protection compiler work
  - reserve / product / service envelopes replay curve/service geometry
  - proper-score / false-positive trust owners replay scorecard, shadow consensus, or robust-stat hazard estimator families

### Decision

- No Round 5 source work, scratch probe, or retained eval was performed.
- The QTRS-seeded lane is retired below target with:
  - incumbent: `screen_0001` / `QuantileTailRiskSketch`
  - incumbent mean edge: `487.54341156295743`
  - best raw: `screen_0004` / `MajorizationRiskVectorFilter`
  - best raw mean edge: `487.7232131981818`
  - best raw gap to breakout target: `2.2767868018182185`
- Search-frame pivot: seed a fresh retained/source lane from Apr21 `screen_0005` / `RegimeSelectorStrongerFloor`, treating it as a floor-preserving seed frame rather than permission for selector coefficient polish.

### Validation And Commands

- Refreshed live run index with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb runs --json`.
- Verified post-Round-4 artifacts before closing the lane:
  - `rtk proxy sh -c 'jq empty artifacts/hill_climb/index.json artifacts/hill_climb/may09-screen490-qtrs-0001/run.json artifacts/hill_climb/may09-screen490-qtrs-0001/results.jsonl artifacts/scratch_probes/may09-screen490-qtrs-0001/round4/*/result.json'`
  - `rtk env UV_CACHE_DIR=.uv-cache uv run pytest tests/test_hill_climb.py -q`
  - `rtk env UV_CACHE_DIR=.uv-cache uv run ruff check tests/test_hill_climb.py`
  - `rtk env UV_CACHE_DIR=.uv-cache uv run ty check tests/test_hill_climb.py`
  - `rtk proxy sh -c 'for f in artifacts/scratch_probes/may09-screen490-qtrs-0001/round4/*/*.sol; do UV_CACHE_DIR=.uv-cache uv run amm-match validate "$f" >/dev/null || exit 1; done'`
  - `rtk git diff --check`

### Updated Entropy Discipline

- Do not spend another QTRS-local batch from `screen_0004` unless the user explicitly reopens this lane with a relaxed banned-family set.
- Keep `screen_0004` as a historical measurement anchor only. It does not clear the breakout target, does not promote over `screen_0001`, and does not repair the floor loss introduced by `screen_0003`.
- The successor lane should start from the floor-selector seed frame and should ban selector coefficient polish, mild fee release, burst-pivot bridge repair, and same-family fee-band polishing from the first proposer pass.
