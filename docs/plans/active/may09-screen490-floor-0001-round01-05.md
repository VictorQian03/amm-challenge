# may09-screen490-floor-0001 rounds 01-05

Run index: [may09-screen490-floor-0001.md](may09-screen490-floor-0001.md)

## Opening State

- Active retained lane: `may09-screen490-floor-0001`.
- Retained seed: `screen_0001` / `seed-from-apr21-screen0005` at `487.01236396243195`.
- Breakout target: `490`.
- Source seed: Apr21 `screen_0005` / `RegimeSelectorStrongerFloor`.
- Prior saturated lane: [may09-screen490-qtrs-0001.md](../completed/may09-screen490-qtrs-0001.md).
- `contracts/src/StarterStrategy.sol` intentionally matches the seed snapshot `3f4bb9e4883515bf62bce866f36815402f6299c9e03b099e1f15f159acec4d9a`.

## Seed Decision

The May09 QTRS-local lane advanced best raw to `screen_0004` / `MajorizationRiskVectorFilter` at `487.7232131981818`, but it remained below the `490` breakout target, did not promote over the QTRS incumbent, and saturated before Round 5 source work. The WCEF `screen_0008` seed frame had already been tried and parked in the May08 lane. This lane deliberately changes seed frame to the older floor-preserving selector anchor instead of continuing QTRS acceleration / vector-order repair or reopening WCEF event-feasibility residual work.

## Carry-Forward Constraints

- Treat `RegimeSelectorStrongerFloor` as the seed frame, not as permission for selector coefficient polish.
- Use `docs/combination_anchor_map.md` for durable saturated-basin and anchor lessons from Apr21, May08, and the May09 QTRS run.
- Keep retained writes serialized through `hill-climb eval`; use `hill-climb probe` for scratch scouting.
- Do not mutate Apr21, May08, or May09 QTRS retained ledgers while continuing this lane.
- Enforce proposer -> critic ordering and require at least four genuinely distinct critic-accepted designs before worker/source edits.
- First proposer pass should exclude selector threshold retuning, mild fee release, burst-pivot bridge repair, same-family fee-band polish, QTRS tail consumer-right replay, WCEF/event-feasibility residual polish, direct fee/base-spread edits, final protection compilers, and broad release deletion.

## Seed Eval

- `screen_0001` / `seed-from-apr21-screen0005`
  - Mean edge: `487.01236396243195`
  - Key profile: `arb_loss_to_retail_gain=0.09201952529170741`, `quote_selectivity_ratio=18.915717013826818`, `time_weighted_mean_fee=0.004864712515229738`
  - Floor slices: `low_decile_mean_edge=371.5875792256349`, `low_retail_mean_edge=416.87678274382506`, `low_volatility_mean_edge=464.14737531113127`
  - Gap to breakout target: `2.98763603756805`

## Validation And Commands

- Restored seed source: `rtk proxy cp artifacts/hill_climb/apr21-screen490-1431/snapshots/3f4bb9e4883515bf62bce866f36815402f6299c9e03b099e1f15f159acec4d9a.sol contracts/src/StarterStrategy.sol`.
- Verified source hash alignment with `shasum -a 256`.
- Revalidated seed source with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match validate contracts/src/StarterStrategy.sol`.
- Seeded retained lane with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb eval --run-id may09-screen490-floor-0001 --stage screen --label seed-from-apr21-screen0005 --json contracts/src/StarterStrategy.sol`.
- Verified live retained state with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb status --run-id may09-screen490-floor-0001 --json`.

## Resume Checklist

- Refresh live state with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb status --run-id may09-screen490-floor-0001 --json`.
- Start Round 1 with a proposer subagent first. It must produce at least six distinct candidates or explicitly declare floor-selector-frame saturation.
- Run the saturation/entropy critic after proposer and before source work. If fewer than four genuinely distinct candidates survive, do not open worker edits.
- Keep accepted worker probes scratch-only under `artifacts/scratch_probes/may09-screen490-floor-0001/round1/`; retained eval is reserved for candidates that beat this lane's live best raw or miss with a genuinely new floor-risk owner and materially better named floor slices.

## Round 1: Floor-Seed Control Batch

### Starting State

- Active retained lane: `may09-screen490-floor-0001`.
- Retained incumbent: `screen_0001` / `seed-from-apr21-screen0005` at `487.01236396243195`.
- Breakout target: `490`.
- Gap to target: `2.98763603756805`.

### Subagent Workflow

- Topology proposer produced six floor-seed candidates:
  - `BarrierCertificateFloorOwner`
  - `CUSUMInnovationSentinel`
  - `MedianOfMeansLiquidityObservation`
  - `LyapunovDriftFloorOwner`
  - `KnockInSideInsurance`
  - `ExecutionPriceResidualCertificate`
- Saturation/entropy critic accepted four and rejected two:
  - Accepted `KnockInSideInsurance`, `CUSUMInnovationSentinel`, `LyapunovDriftFloorOwner`, and `BarrierCertificateFloorOwner`.
  - Rejected `MedianOfMeansLiquidityObservation` as robust-demand / median-of-means replay.
  - Rejected `ExecutionPriceResidualCertificate` as WCEF/event-feasibility residual polish plus source-deconvolution / generic uncertainty-label hidden-release risk.
- Enforced entropy constraints:
  - at least four critic-accepted designs before source work
  - scratch-only worker scope under this run's `round1/` directory
  - no selector threshold retuning, mild fee release, burst-pivot bridge repair, same-family fee-band polish, QTRS tail consumer-right replay, WCEF/event-feasibility residual polish, direct fee/base-spread edits, final protection compilers, or broad release deletion

### Probe Sources

- `artifacts/scratch_probes/may09-screen490-floor-0001/round1/knock_in_side_insurance/StarterStrategy.sol`
- `artifacts/scratch_probes/may09-screen490-floor-0001/round1/cusum_innovation_sentinel/StarterStrategy.sol`
- `artifacts/scratch_probes/may09-screen490-floor-0001/round1/lyapunov_drift_floor_owner/StarterStrategy.sol`
- `artifacts/scratch_probes/may09-screen490-floor-0001/round1/barrier_certificate_floor_owner/StarterStrategy.sol`

### Probe Results

- `KnockInSideInsurance`
  - Mean edge: `487.01236396243195`
  - Delta vs seed: `0.0`
  - Key profile: `arb_loss_to_retail_gain=0.09201952529170741`, `quote_selectivity_ratio=18.915717013826818`, `time_weighted_mean_fee=0.004864712515229738`
  - Floor slices: `low_decile_mean_edge=371.5875792256349`, `low_retail_mean_edge=416.87678274382506`, `low_volatility_mean_edge=464.14737531113127`
  - Outcome: killed as exact phenotype replay / no-op side-insurance activation.
- `CUSUMInnovationSentinel`
  - Mean edge: `460.3501840073978`
  - Delta vs seed: `-26.662179955034162`
  - Key profile: `arb_loss_to_retail_gain=0.132177576585676`, `quote_selectivity_ratio=26.14188220993261`, `time_weighted_mean_fee=0.005056161431844227`
  - Floor slices: `low_decile_mean_edge=281.2031206196539`, `low_retail_mean_edge=399.4400992998129`, `low_volatility_mean_edge=437.66323665596104`
  - Outcome: killed as process-control overprotection / leakage and floor collapse.
- `LyapunovDriftFloorOwner`
  - Mean edge: `408.1365175758138`
  - Delta vs seed: `-78.87584638661815`
  - Key profile: `arb_loss_to_retail_gain=0.25057671287377087`, `quote_selectivity_ratio=66.94073831894647`, `time_weighted_mean_fee=0.0037432618636482717`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=362.0770348063131`, `low_volatility_mean_edge=415.8239352813685`
  - Outcome: killed as Lyapunov energy hidden release / severe floor collapse.
- `BarrierCertificateFloorOwner`
  - Mean edge: `473.4961780513568`
  - Delta vs seed: `-13.516185911075127`
  - Key profile: `arb_loss_to_retail_gain=0.11590770970279574`, `quote_selectivity_ratio=23.618341417108404`, `time_weighted_mean_fee=0.004907529604040516`
  - Floor slices: `low_decile_mean_edge=304.31962571993324`, `low_retail_mean_edge=397.7992251987958`, `low_volatility_mean_edge=462.6287682937878`
  - Outcome: killed as barrier-certificate hidden-release / floor damage despite bounded one-way intent.

### Decision

- No Round 1 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001` / `RegimeSelectorStrongerFloor`
  - best raw in the May09 floor-seed lane: `screen_0001`
  - best raw mean edge: `487.01236396243195`
  - gap to breakout target: `2.98763603756805`

### Validation And Commands

- Validated all four accepted scratch sources with `rtk proxy sh -c 'for f in artifacts/scratch_probes/may09-screen490-floor-0001/round1/*/StarterStrategy.sol; do UV_CACHE_DIR=.uv-cache uv run amm-match validate "$f" >/dev/null || exit 1; done'`.
- Ran each scratch probe with `rtk proxy sh -c 'UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb probe --stage screen --json <source> > <result.json>'`.
- No retained eval was spent because none beat live best raw or repaired floor slices.

### Updated Entropy Discipline

- The first floor-seed batch did not break out. Knock-in side insurance was exact no-op; CUSUM/process-control, Lyapunov energy, and barrier certificates collapsed into leakage/selectivity and floor failures.
- Do not continue side-insurance knock-in, process-control innovation accumulation, Lyapunov energy/drift, or barrier-certificate floor owners unless the next proposal names a different downstream consumer contract that cannot feed release or overprotection.
- Keep the rejected robust-demand / median-of-means and execution-price residual families excluded.
- Round 2 must start from a new proposer -> critic pass and should bias away from add-only hazard/side-risk evidence that still flows through the current downstream consumers.

## Round 2: Subagent Availability Blocker

### Starting State

- Active retained lane: `may09-screen490-floor-0001`.
- Retained incumbent: `screen_0001` / `seed-from-apr21-screen0005` at `487.01236396243195`.
- Best raw before the round: `screen_0001`.
- Breakout target: `490`.
- Gap to target: `2.98763603756805`.

### Blocker

- The coordinator attempted to start the Round 2 proposer subagent after Round 1 notes and anchor-map lessons were updated.
- The subagent failed before producing a proposal due the current account usage limit.
- Platform reset message: try again at `2026-05-09 07:24` local app time.
- No Round 2 proposal, critic review, scratch source work, or retained eval was performed.
- The prescribed workflow remains blocked at proposer-first ordering; do not bypass it with local-only source edits.
- The coordinator retried the required proposer subagent at `2026-05-09 04:14 CEST` using the ready proposer prompt below; the platform returned the same usage-limit reset message and no proposal was produced.

### Continuation Constraint

- The next proposer -> critic pass must exclude:
  - Round 1 floor-seed failures: side-insurance knock-in, process-control innovation accumulation, Lyapunov energy/drift, and barrier-certificate floor owners
  - rejected Round 1 families: robust-demand / median-of-means and execution-price residual / WCEF residual / source-deconvolution
  - previously saturated May09 QTRS families: QTRS tail consumer-right rewires, flow-share entropy, response-elasticity side-risk, fixed-mass protection routing, adverse/benign classifier bases, signed-impact bus, invariant/geometry codec, volatility acceleration pulse/cap polish, duration occupancy, benign microtrade caps, credit-stack exclusivity, stress quorum/conjunction, protection continuity debt, false-positive scorecards, shadow consensus bands, vector-order side filters, and anti-windup memory writes
  - May08 WCEF/event-feasibility residual polish, selector threshold retuning, mild fee release, burst-pivot bridge repair, same-family fee-band polish, direct fee/base-spread edits, final protection compilers, broad release deletion, curve/service geometry, typed shock co-occurrence, and weak-anchor stacking
- Bias the next batch toward new downstream consumer contracts or mechanical isolation that changes how evidence is consumed, not another label routed into the same hazard/side-risk consumers.

### Resume Checklist

- Refresh live state with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb status --run-id may09-screen490-floor-0001 --json`.
- Confirm source alignment before source work: `contracts/src/StarterStrategy.sol` intentionally matches active seed snapshot `3f4bb9e4883515bf62bce866f36815402f6299c9e03b099e1f15f159acec4d9a`.
- Restart with a proposer subagent first. It must produce at least six distinct candidates or explicitly declare floor-selector-frame saturation.
- Run the saturation/entropy critic after proposer and before source work. If fewer than four genuinely distinct candidates survive, do not open worker edits.
- Keep any accepted worker probes scratch-only under `artifacts/scratch_probes/may09-screen490-floor-0001/round2/`; retained eval is reserved for candidates that beat the active run's live best raw or miss with a genuinely new floor-risk owner and materially better named floor slices.

### Ready Proposer Prompt

Use this as the first post-reset subagent prompt:

```text
You are the Round 2 topology proposer for the active simple_amm hill-climb run `may09-screen490-floor-0001`. Do not edit files.

Live state to preserve:
- Target breakout: 490.
- Active seed/incumbent/best raw: `screen_0001` / `seed-from-apr21-screen0005` / `LatentStateQuoteEngine`.
- Current mean edge: 487.01236396243195.
- Gap to breakout target: 2.98763603756805.
- The retained lane is append-only; workers must stay scratch-only until critic acceptance and coordinator assignment.

Round 1 floor-seed failures to exclude:
- side-insurance knock-in, which was an exact no-op phenotype replay.
- process-control innovation accumulation, which overprotected and damaged floors.
- Lyapunov energy/drift owners, which caused severe hidden-release floor collapse.
- barrier-certificate floor owners, which still damaged low-decile and retail floors.
- robust-demand / median-of-means.
- execution-price residual / WCEF residual / source-deconvolution.

Previously saturated families to exclude:
- QTRS tail consumer-right rewires, flow-share entropy, response-elasticity side-risk, fixed-mass protection routing, adverse/benign classifier bases, signed-impact bus, invariant/geometry codec, volatility acceleration pulse/cap polish, duration occupancy, benign microtrade caps, credit-stack exclusivity, stress quorum/conjunction, protection continuity debt, false-positive scorecards, shadow consensus bands, vector-order side filters, anti-windup memory writes.
- May08 WCEF/event-feasibility residual polish, selector threshold retuning, mild fee release, burst-pivot bridge repair, same-family fee-band polish, direct fee/base-spread edits, final protection compilers, broad release deletion, curve/service geometry, typed shock co-occurrence, weak-anchor stacking.

Output at least six genuinely distinct strategy-design candidates or explicitly declare floor-selector-frame saturation. Each candidate must name:
- the new downstream consumer contract or mechanical isolation it introduces;
- why it is not routed through the same failed hazard/side-risk consumers;
- the expected scorecard movement on mean edge, leakage/selectivity, low-decile, low-retail, and low-volatility slices;
- the concrete reason it should survive the critic entropy gate.
```

### Ready Critic Prompt

Use this immediately after the proposer returns candidates:

```text
You are the Round 2 saturation and entropy critic for the active simple_amm hill-climb run `may09-screen490-floor-0001`. Do not edit files.

Review the proposer output against the active run note and combination anchor map. Enforce the hard exclusions exactly:
- reject Round 1 floor-seed replays: side-insurance knock-in, process-control innovation accumulation, Lyapunov energy/drift, barrier-certificate floor owners, robust-demand / median-of-means, execution-price residual / WCEF residual / source-deconvolution.
- reject saturated May09 QTRS and May08 WCEF families listed in the Round 2 continuation constraint.
- reject candidates that add another hazard/side-risk label while leaving the same downstream consumer contract intact.
- reject coefficient, threshold, fee-band, release, base-spread, or final-compiler polish unless the candidate also introduces a genuinely new downstream consumer contract or mechanical isolation.

Return:
- accepted candidates, with at least four required before worker edits may begin;
- rejected candidates, each with the precise saturation family or failure phenotype;
- an entropy verdict explaining whether the accepted set spans distinct abstractions, topologies, designs, and estimations;
- a stop verdict if fewer than four candidates survive, instructing the coordinator to request another proposer pass instead of opening source work.
```

### Ready Worker Prompt

Use this only after the critic accepts at least four genuinely distinct candidates. Assign one accepted candidate and one unique scratch path per worker:

```text
You are a Round 2 scratch-only strategy worker for `may09-screen490-floor-0001`. You are not alone in the codebase; other workers may edit separate scratch paths. Do not edit or revert their files.

Ownership:
- Accepted candidate: <candidate name and critic-approved contract>.
- Write scope: `artifacts/scratch_probes/may09-screen490-floor-0001/round2/<candidate_slug>/StarterStrategy.sol`.
- Do not edit `contracts/src/StarterStrategy.sol`, `artifacts/hill_climb/**`, run ledgers, docs, or any other worker path.

Starting point:
- Copy the active seed strategy into your assigned scratch path, then implement only the accepted topology contract.
- Preserve the candidate's distinct downstream consumer contract or mechanical isolation; do not collapse into excluded families or coefficient polish.

Validation:
- Run `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match validate <your scratch source>`.
- Run `rtk proxy sh -c 'UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb probe --stage screen --json <your scratch source> > <your scratch result.json>'`.
- Inspect mean edge, leakage/selectivity, low-decile, low-retail, and low-volatility slices against the active seed `487.01236396243195`.

Return:
- changed file path;
- validation commands and outcomes;
- probe result path;
- mean edge and delta vs seed;
- named failure/success phenotype;
- whether the candidate deserves coordinator consideration for a retained eval. Do not run retained `hill-climb eval`.
```

## Round 2 Resumed: OOD Upstream Transform Batch

### Search Correction

- The first resumed proposer attempt was stopped because its web/literature sources and candidate shapes repeated prior AMM, LOB, WCEF, QTRS, hazard, release, and consumer-wiring failure modes.
- A read-only gap audit identified the true saturated classes before source work: WCEF sensor floors and consumer rewires, QTRS tail/side-risk/vector-order repair, scorecard/trust/classifier surfaces, attribution/source labels, queue/depth/latency imports, service/allocation/direct-fee/relief surfaces, and Round 1 add-only control families.
- A second OOD pass using runtime assurance, command governors, CPPI/TIPP, privacy odometers, tube control, and relay vocabulary was rejected by the critic because all accepted-looking ideas collapsed into opportunity-cut / release governors under different names.
- A third proposer pass banned opportunity cuts, release, refill, recapture, calm bonus, passive recapture, inventory centering, final quote, direct fee/base-spread, relief deletion, and command-governor surfaces. It used genuinely OOD vocabulary from physical reservoir computing, artificial immune danger theory, ecological critical slowing down, and error-correcting codes, but only accepted ideas with upstream or protection-sizing ownership.

### Subagent Workflow

- Proposer pass 3 produced six candidates:
  - `FixedReservoirObservationReadout`
  - `RecoveryHalfLifeHazardDecay`
  - `SlowManifoldLatentProjector`
  - `DangerTensorRiskDecomposition`
  - `ConstantNormCodewordSideTransform`
  - `DangerSafeMemoryWriteMux`
- Saturation/entropy critic accepted five and rejected one:
  - Accepted `FixedReservoirObservationReadout`, `RecoveryHalfLifeHazardDecay`, `SlowManifoldLatentProjector`, `DangerTensorRiskDecomposition`, and `DangerSafeMemoryWriteMux`.
  - Rejected `ConstantNormCodewordSideTransform` as bid/ask side-risk / vector-order replay despite its fixed-total guard.
- Enforced entropy constraints:
  - no worker edits until at least four critic-accepted candidates survived
  - scratch-only worker paths under `artifacts/scratch_probes/may09-screen490-floor-0001/round2/`
  - no retained-ledger writes by workers
  - no edits to `contracts/src/StarterStrategy.sol`
  - no opportunity/release/final-quote/direct-fee/refill/recapture/calm-bonus surfaces

### Probe Sources

- `artifacts/scratch_probes/may09-screen490-floor-0001/round2/fixed_reservoir_observation_readout/StarterStrategy.sol`
- `artifacts/scratch_probes/may09-screen490-floor-0001/round2/recovery_half_life_hazard_decay/StarterStrategy.sol`
- `artifacts/scratch_probes/may09-screen490-floor-0001/round2/slow_manifold_latent_projector/StarterStrategy.sol`
- `artifacts/scratch_probes/may09-screen490-floor-0001/round2/danger_tensor_risk_decomposition/StarterStrategy.sol`
- `artifacts/scratch_probes/may09-screen490-floor-0001/round2/danger_safe_memory_write_mux/StarterStrategy.sol`

### Probe Results

- `FixedReservoirObservationReadout`
  - Mean edge: `456.35751896270375`
  - Delta vs seed: `-30.654844999728198`
  - Key profile: `arb_loss_to_retail_gain=0.149059986631203`, `quote_selectivity_ratio=32.161624742417764`, `time_weighted_mean_fee=0.004634715684453862`
  - Floor slices: `low_decile_mean_edge=263.151432051347`, `low_retail_mean_edge=399.0872298623463`, `low_volatility_mean_edge=440.5300053804212`
  - Outcome: killed as fixed-reservoir upstream hidden release / low-decile collapse.
- `RecoveryHalfLifeHazardDecay`
  - Mean edge: `424.28771550969094`
  - Delta vs seed: `-62.72464845274101`
  - Key profile: `arb_loss_to_retail_gain=0.2163998642410846`, `quote_selectivity_ratio=52.768028898302525`, `time_weighted_mean_fee=0.004100965466383867`
  - Floor slices: `low_decile_mean_edge=232.9934650368802`, `low_retail_mean_edge=377.13618386718866`, `low_volatility_mean_edge=415.8084495539634`
  - Outcome: killed as recovery-half-life hidden release / severe floor collapse.
- `SlowManifoldLatentProjector`
  - Mean edge: `475.42956850998155`
  - Delta vs seed: `-11.5827954524504`
  - Key profile: `arb_loss_to_retail_gain=0.11829050709699512`, `quote_selectivity_ratio=26.049509002244573`, `time_weighted_mean_fee=0.00454098797358532`
  - Floor slices: `low_decile_mean_edge=305.06975681418095`, `low_retail_mean_edge=399.755140010988`, `low_volatility_mean_edge=465.3959170726186`
  - Outcome: killed as slow-manifold latent catch-up hidden release; low-volatility improved, but low-decile / low-retail and leakage failed.
- `DangerTensorRiskDecomposition`
  - Mean edge: `424.61002918446053`
  - Delta vs seed: `-62.40233477797142`
  - Key profile: `arb_loss_to_retail_gain=0.21403200031331465`, `quote_selectivity_ratio=51.06237561511332`, `time_weighted_mean_fee=0.004191579371993926`
  - Floor slices: `low_decile_mean_edge=232.98456952792287`, `low_retail_mean_edge=377.44194737644597`, `low_volatility_mean_edge=416.3091868660879`
  - Outcome: killed as danger-tensor hidden release / high-selectivity floor collapse.
- `DangerSafeMemoryWriteMux`
  - Mean edge: `421.50303121873316`
  - Delta vs seed: `-65.50933274369879`
  - Key profile: `arb_loss_to_retail_gain=0.22123313497988834`, `quote_selectivity_ratio=53.64837614886943`, `time_weighted_mean_fee=0.0041237620010340335`
  - Floor slices: `low_decile_mean_edge=223.66154433493614`, `low_retail_mean_edge=375.21543034507`, `low_volatility_mean_edge=415.8084471537558`
  - Outcome: killed as danger/safe write-routing hidden release / severe floor collapse.

### Decision

- No Round 2 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001` / `RegimeSelectorStrongerFloor`
  - best raw in the May09 floor-seed lane: `screen_0001`
  - best raw mean edge: `487.01236396243195`
  - gap to breakout target: `2.98763603756805`

### Validation And Commands

- Validated all five accepted scratch sources with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match validate <scratch source>`.
- Ran each scratch probe with `rtk proxy sh -c 'UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb probe --stage screen --json <source> > <result.json>'`.
- Verified retained state remained unchanged with `rtk env UV_CACHE_DIR=.uv-cache uv run amm-match hill-climb status --run-id may09-screen490-floor-0001`.
- Verified seed source remained aligned with retained snapshot using `rtk shasum -a 256 contracts/src/StarterStrategy.sol artifacts/hill_climb/may09-screen490-floor-0001/snapshots/3f4bb9e4883515bf62bce866f36815402f6299c9e03b099e1f15f159acec4d9a.sol`.

### Updated Entropy Discipline

- OOD vocabulary alone remains insufficient. Physical-reservoir, ecological, and immune-system imports all failed once their upstream changes flowed into the current floor-seed hazard/protection path.
- Do not continue fixed reservoir readouts, recovery-half-life memory persistence, slow-manifold latent catch-up, danger-tensor risk decomposition, or danger/safe memory write routing under the current floor seed unless a future search-frame change provides a new downstream owner that cannot become low-fee hidden release.
- The one weak positive observed in Round 2 was `SlowManifoldLatentProjector` improving `low_volatility_mean_edge`; it still failed mean, leakage/selectivity, low-decile, and low-retail badly, so it is not a support anchor.
- The next proposer pass should either change the seed/search frame again or name a mechanism whose owner is not upstream observation shaping, memory persistence, latent recentering, deterministic danger tensors, or write-routing into the existing hazard/protection path.

## Round 3 Readiness

- Retained state is unchanged after Round 2: active incumbent and best raw are both `screen_0001` / `RegimeSelectorStrongerFloor` at `487.01236396243195`.
- `contracts/src/StarterStrategy.sol` should remain byte-for-byte aligned with snapshot `3f4bb9e4883515bf62bce866f36815402f6299c9e03b099e1f15f159acec4d9a.sol` before any new scratch work.
- Start Round 3 with the proposal scorecard in `docs/hill_climb.md` and `docs/combination_anchor_map.md`; do not accept another OOD label unless it names the new consumer contract, forbidden readers, nearest negative example, metric budget, and kill signature.
- If no four-design batch survives those checks, record floor-seed saturation or explicitly choose a search-frame change instead of padding the batch with more upstream labels.
