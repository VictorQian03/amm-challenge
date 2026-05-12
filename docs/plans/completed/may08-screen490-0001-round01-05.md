# may08-screen490-0001 rounds 01-05

Run index: [may08-screen490-0001.md](may08-screen490-0001.md)

## Opening State

- Active retained lane: `may08-screen490-0001`.
- Retained seed: `screen_0001` / `seed-from-apr21-screen0008` at `488.03274719863765`.
- Breakout target: `490`.
- Source seed: Apr21 `screen_0008` / `weak-consistency-event-feasibility-mask`.
- Prior lane archive: [apr21-screen490-1431.md](../completed/apr21-screen490-1431.md).

## Seed Decision

The Apr21 lane saturated below target after Round 48. The May08 lane starts from the best measured Apr21 raw anchor rather than continuing to append scratch-only rounds to a historical lane.

## Carry-Forward Constraints

- Treat `WeakConsistencyEventFeasibilityMask` as the incumbent seed, not as permission for local event-feasibility residual coefficient tuning.
- Use `docs/combination_anchor_map.md` for durable saturated-basin and anchor lessons from Apr21.
- Keep retained writes serialized through `hill-climb eval`; use `hill-climb probe` for scratch scouting.
- Do not mutate Apr21 retained ledgers while continuing this lane.

## Round 1: Post-WCEF Sensor And Risk-Composition Batch

### Starting State

- Active retained lane: `may08-screen490-0001`.
- Retained incumbent: `screen_0001` / `seed-from-apr21-screen0008` at `488.03274719863765`.
- Breakout target: `490`.
- Gap to target: `1.9672528013623468`.
- Before source work, the checked-out `contracts/src/StarterStrategy.sol` did not match the retained May08 seed. The coordinator restored the retained screen incumbent with `hill-climb pull-best` and revalidated it as `WeakConsistencyEventFeasibilityMask`.

### Subagent Workflow

- Topology proposer produced eight high-entropy contracts across layer-1 shock sensing, layer-2 rail coding / phase-plane / mechanics, layer-3 barrier certificates, layer-4 max-plus composition, event-body saturation, and one bounded layer-5 diagnostic.
- Saturation critic accepted six and rejected two:
  - Accepted `WENOShockSensor`, `SyndromeProtectedTripletCode`, `PhasePlaneCurlWitness`, `BarrierCertificateRiskFloor`, `MaxPlusRiskAssembler`, and `ElasticEnergyReservoir`.
  - Rejected `SensorSaturationBifurcator` as scalar event-body / fee-path tuning risk.
  - Rejected `ComplementCascadeSeal` as too close to WCEF tail / residual refinement.
- Enforced entropy constraints:
  - at least four critic-accepted designs before worker edits
  - no retained-ledger edits by workers
  - no `Reference.sol` inspection
  - no weak-consistency residual coefficient tuning, retained-snapshot union, service-capacity repair, queue/depth/passive-fill/latency, temporal clocks, direct fee rights, final quote, refill/recapture/opportunity replay, relief deletion, account/allocation/cost-share vocabulary, causal/adverse-mass labels, generic uncertainty labels, robust-demand bins, liquidity-shortfall placement, source deconvolution, run-length/context segment labels, or scalar hazard damping

### Probe Sources

- `artifacts/scratch_probes/may08-screen490-0001/round1/weno_shock_sensor/weno_shock_sensor.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round1/syndrome_protected_triplet_code/syndrome_protected_triplet_code.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round1/phase_plane_curl_witness/phase_plane_curl_witness.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round1/barrier_certificate_risk_floor/barrier_certificate_risk_floor.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round1/max_plus_risk_assembler/max_plus_risk_assembler.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round1/elastic_energy_reservoir/elastic_energy_reservoir.sol`

### Probe Results

- `WENOShockSensor`
  - Mean edge: `447.48658709319204`
  - Delta vs seed: `-40.54616010544561`
  - Key profile: `arb_loss_to_retail_gain=0.16848211332980667`, `quote_selectivity_ratio=37.85813584558672`, `time_weighted_mean_fee=0.004450354185874351`
  - Floor slices: `low_decile_mean_edge=250.47469282862278`, `low_retail_mean_edge=399.916769561561`, `low_volatility_mean_edge=416.7339294034042`
  - Outcome: killed as sensor-floor hidden release / floor collapse.
- `SyndromeProtectedTripletCode`
  - Mean edge: `473.7080001583925`
  - Delta vs seed: `-14.324747040245142`
  - Key profile: `arb_loss_to_retail_gain=0.11571261853956069`, `quote_selectivity_ratio=24.198887421019442`, `time_weighted_mean_fee=0.004781732999801112`
  - Floor slices: `low_decile_mean_edge=291.9717775525282`, `low_retail_mean_edge=399.8904578176999`, `low_volatility_mean_edge=465.1871007698987`
  - Outcome: killed as rail-agreement hidden release / low-decile and low-retail floor collapse.
- `PhasePlaneCurlWitness`
  - Mean edge: `444.8481009282063`
  - Delta vs seed: `-43.18464627043136`
  - Key profile: `arb_loss_to_retail_gain=0.16974493289871748`, `quote_selectivity_ratio=36.78965422410018`, `time_weighted_mean_fee=0.004613931184694878`
  - Floor slices: `low_decile_mean_edge=250.47469282862278`, `low_retail_mean_edge=399.7069588133026`, `low_volatility_mean_edge=416.78157994331525`
  - Outcome: killed as phase-plane side-hazard hidden release / floor collapse.
- `BarrierCertificateRiskFloor`
  - Mean edge: `455.4564026390169`
  - Delta vs seed: `-32.57634455962074`
  - Key profile: `arb_loss_to_retail_gain=0.1437874565130861`, `quote_selectivity_ratio=29.200100223701803`, `time_weighted_mean_fee=0.0049242110613159275`
  - Floor slices: `low_decile_mean_edge=251.6397402093046`, `low_retail_mean_edge=399.4059012742782`, `low_volatility_mean_edge=440.5623476283845`
  - Outcome: killed as barrier-certificate hidden release / floor collapse.
- `MaxPlusRiskAssembler`
  - Mean edge: `488.01235488980313`
  - Delta vs seed: `-0.020392308834515114`
  - Key profile: `arb_loss_to_retail_gain=0.0878280145206823`, `quote_selectivity_ratio=17.69866500389364`, `time_weighted_mean_fee=0.004962409000981738`
  - Floor slices: `low_decile_mean_edge=372.204660495869`, `low_retail_mean_edge=417.8844807190404`, `low_volatility_mean_edge=465.275575613975`
  - Outcome: killed as sub-seed risk-composition reshuffle with worse leakage/selectivity; no retained eval.
- `ElasticEnergyReservoir`
  - Mean edge: `488.03274706699267`
  - Delta vs seed: `-0.00000013164498114205`
  - Key profile: `arb_loss_to_retail_gain=0.08680487737035317`, `quote_selectivity_ratio=17.374961467424928`, `time_weighted_mean_fee=0.004995975244785286`
  - Floor slices: `low_decile_mean_edge=372.41890882964583`, `low_retail_mean_edge=417.8656702477847`, `low_volatility_mean_edge=465.187105764097`
  - Outcome: killed as phenotype-identical mechanics reservoir no-op.

### Decision

- No Round 1 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw in the May08 lane: `screen_0001`
  - best raw mean edge: `488.03274719863765`
  - gap to breakout target: `1.9672528013623468`

### Validation And Commands

- Restored retained seed: `uv run amm-match hill-climb pull-best --run-id may08-screen490-0001 --stage screen --destination contracts/src/StarterStrategy.sol`.
- Revalidated retained seed: `uv run amm-match validate contracts/src/StarterStrategy.sol`.
- Validated all six accepted scratch sources with `uv run amm-match validate`.
- Ran each scratch probe with `uv run amm-match hill-climb probe --stage screen --json <source>` and wrote the JSON result beside the source.

### Updated Entropy Discipline

- Under the WCEF seed, adding new one-way layer-1/2/3 sensor floors into the existing monotone / hazard / side-risk consumer path often becomes low-fee hidden release: WENO shock smoothness, triplet-code rail agreement, phase-plane curl, and barrier certificate all lowered fee band, increased leakage/selectivity, and broke low-decile / low-retail floors.
- `MaxPlusRiskAssembler` showed that risk-composition reshuffling is not enough by itself; it stayed near the seed but worsened leakage/selectivity and mean.
- `ElasticEnergyReservoir` was effectively phenotype-identical, so bounded mechanics-reservoir floors are not a useful primary owner without a different downstream consumer.
- Next batch should avoid more WCEF-adjacent sensor floors unless the proposal changes the downstream consumer contract, not just the upstream evidence vocabulary. Any new upstream signal must prove it cannot enter existing release / rebate / opportunity / refill / calm paths indirectly.

## Round 2: Consumer-Contract Isolation Batch

### Starting State

- Active retained lane: `may08-screen490-0001`.
- Retained incumbent: `screen_0001` / `seed-from-apr21-screen0008` at `488.03274719863765`.
- Breakout target: `490`.
- Round 1 closed with no retained eval and a new constraint: no more upstream WCEF-adjacent sensor floors unless the downstream consumer contract changes mechanically.

### Subagent Workflow

- Topology proposer produced seven consumer-contract candidates that shifted from new sensors toward downstream isolation:
  - `FeasibilityHoldOnlyBus`
  - `CalmProvenanceSeal`
  - `CommitAfterPricingBarrier`
  - `TypedSpreadAtomCutCap`
  - `OneSideRiskMuxNoSharedWidth`
  - `DivergenceWriteLock`
  - `KirchhoffCutDiode`
- Saturation critic accepted six and rejected `OneSideRiskMuxNoSharedWidth` as overlapping the same consumer-isolation topology as `FeasibilityHoldOnlyBus`.
- Enforced entropy constraints:
  - six critic-accepted designs before source work
  - no retained-ledger edits by workers
  - no `Reference.sol` inspection
  - no upstream sensor-floor retry without downstream consumer isolation
  - one bounded layer 5/6 diagnostic only: `KirchhoffCutDiode`

### Probe Sources

- `artifacts/scratch_probes/may08-screen490-0001/round2/feasibility_hold_only_bus/feasibility_hold_only_bus.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round2/calm_provenance_seal/calm_provenance_seal.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round2/commit_after_pricing_barrier/commit_after_pricing_barrier.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round2/typed_spread_atom_cut_cap/typed_spread_atom_cut_cap.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round2/divergence_write_lock/divergence_write_lock.sol`
- `artifacts/scratch_probes/may08-screen490-0001/round2/kirchhoff_cut_diode/kirchhoff_cut_diode.sol`

### Probe Results

- `FeasibilityHoldOnlyBus`
  - Mean edge: `487.64576622544377`
  - Delta vs seed: `-0.3869809731938772`
  - Key profile: `arb_loss_to_retail_gain=0.09149331332731843`, `quote_selectivity_ratio=18.932509842444244`, `time_weighted_mean_fee=0.004832603499943902`
  - Floor slices: `low_decile_mean_edge=372.1865068927169`, `low_retail_mean_edge=417.627241024482`, `low_volatility_mean_edge=465.05802600570917`
  - Outcome: killed as lower-fee hidden release with worse leakage/selectivity and sub-seed mean.
- `CalmProvenanceSeal`
  - Mean edge: `483.90481845102295`
  - Delta vs seed: `-4.127928747614704`
  - Key profile: `arb_loss_to_retail_gain=0.08760810136509675`, `quote_selectivity_ratio=16.70423497611614`, `time_weighted_mean_fee=0.005244664092091591`
  - Floor slices: `low_decile_mean_edge=368.50784236256436`, `low_retail_mean_edge=413.8388728331222`, `low_volatility_mean_edge=460.68620234102406`
  - Outcome: killed as calm-provenance overcharge / floor loss.
- `CommitAfterPricingBarrier`
  - Mean edge: `481.85936133134925`
  - Delta vs seed: `-6.1733858672884`
  - Key profile: `arb_loss_to_retail_gain=0.09972586457651997`, `quote_selectivity_ratio=20.384312896487277`, `time_weighted_mean_fee=0.004892284821319889`
  - Floor slices: `low_decile_mean_edge=331.11029892293953`, `low_retail_mean_edge=399.9047891277997`, `low_volatility_mean_edge=465.20121539135204`
  - Outcome: killed as post-pricing commit barrier hidden release / low-decile collapse.
- `TypedSpreadAtomCutCap`
  - Mean edge: `480.5707434573276`
  - Delta vs seed: `-7.462003741310047`
  - Key profile: `arb_loss_to_retail_gain=0.08617696283035303`, `quote_selectivity_ratio=15.69099648817881`, `time_weighted_mean_fee=0.005492128106412905`
  - Floor slices: `low_decile_mean_edge=366.5548578895208`, `low_retail_mean_edge=411.3672777610702`, `low_volatility_mean_edge=457.5793089219622`
  - Outcome: killed as spread-atom overcharge / benign-capture starvation despite better leakage/selectivity.
- `DivergenceWriteLock`
  - Mean edge: `488.032712784516`
  - Delta vs seed: `-0.000034414121654475864`
  - Key profile: `arb_loss_to_retail_gain=0.08680472776262455`, `quote_selectivity_ratio=17.374910061864618`, `time_weighted_mean_fee=0.0049959814153598524`
  - Floor slices: `low_decile_mean_edge=372.41891383000967`, `low_retail_mean_edge=417.86555004252244`, `low_volatility_mean_edge=465.1869817943525`
  - Outcome: killed as phenotype-identical divergence write-lock no-op.
- `KirchhoffCutDiode`
  - Mean edge: `444.98216080543716`
  - Delta vs seed: `-43.05058639320049`
  - Key profile: `arb_loss_to_retail_gain=0.1725989119978337`, `quote_selectivity_ratio=38.45386019037529`, `time_weighted_mean_fee=0.0044884677674319395`
  - Floor slices: `low_decile_mean_edge=250.47469282862278`, `low_retail_mean_edge=399.9468014002168`, `low_volatility_mean_edge=416.7747518727593`
  - Outcome: killed as cut-conductance hidden release / floor collapse.

### Decision

- No Round 2 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw in the May08 lane: `screen_0001`
  - best raw mean edge: `488.03274719863765`
  - gap to breakout target: `1.9672528013623468`

### Validation And Commands

- Validated all six accepted scratch sources with `uv run amm-match validate`.
- Ran each scratch probe with `uv run amm-match hill-climb probe --stage screen --json <source>` and wrote the JSON result beside the source.

### Updated Entropy Discipline

- Consumer-contract isolation around the current WCEF seed still did not break out. `FeasibilityHoldOnlyBus` was the nearest miss, but it lowered fees, worsened leakage/selectivity, and stayed `0.38698` below seed.
- `DivergenceWriteLock` confirms that same-swap divergence write ordering is not a productive primary owner under this seed; it was effectively phenotype-identical.
- Cut gating and atom typing are dangerous in this neighborhood: `TypedSpreadAtomCutCap` overcharged into benign-capture starvation, while `KirchhoffCutDiode` cut conductance collapsed into lower-fee hidden release.
- The next batch should not keep rearranging WCEF consumer wiring unless it introduces a primary owner outside monotone evidence, calm provenance, cut eligibility, latent commit order, spread atoms, and divergence writes.

## Round 3: Entropy Blocker Before Source Work

### Starting State

- Active retained lane: `may08-screen490-0001`.
- Retained incumbent: `screen_0001` / `seed-from-apr21-screen0008` at `488.03274719863765`.
- Breakout target: `490`.
- Rounds 1-2 exhausted post-WCEF sensor floors and WCEF consumer-contract rearrangements without producing a retained candidate.

### Subagent Workflow

- Topology proposer was asked to generate at least six candidates outside:
  - monotone evidence
  - WCEF sensor floors
  - hazard/calm side-risk consumer rearrangement
  - cut eligibility
  - latent commit order
  - spread atoms
  - divergence writes
  - service-capacity repair
  - retained-snapshot unions
  - queue/depth/passive-fill/latency
  - temporal clocks
  - final quote
  - direct fee rights
  - refill/recapture/opportunity replay
  - relief deletion
  - account/allocation/cost-share vocabulary
  - causal/adverse-mass labels
  - generic uncertainty labels
  - robust-demand bins
  - liquidity-shortfall placement
  - source deconvolution
  - run-length/context segment labels
  - scalar hazard damping
- The proposer could not defend four genuinely distinct positive-expected designs under that exclusion set.

### Blocker

- Remaining local surfaces collapse into already killed classes:
  - coordinate / geometry remaps replay upstream geometry-codec or invariant-hold plateaus
  - state-write / EMA changes replay divergence writes, scalar damping, or no-op memory polish
  - fee projection, relief clamps, and benign-capture preservation touch banned final quote, direct fee rights, spread atoms, relief deletion, or consumer rearrangement
  - OOD market-design imports already failed as service-capacity, reserve-score, priority / waterfall, or snapshot-union variants
  - new labels violate the bans on generic uncertainty, causal/adverse mass, robust demand, source deconvolution, run-length/context, liquidity shortfall, queue/depth/latency, or WCEF-adjacent floors
- No Round 3 scratch source work was started.
- No retained eval was spent.

### Decision

- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw in the May08 lane: `screen_0001`
  - best raw mean edge: `488.03274719863765`
  - gap to breakout target: `1.9672528013623468`
- The next harness-consistent move is a search-frame change rather than naming-churn probes: import fresh outside mechanism vocabulary or change the seed / anchor frame before more worker source edits.
