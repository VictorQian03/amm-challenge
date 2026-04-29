# apr21-screen490-1431 rounds 31-35

Run index: [apr21-screen490-1431.md](apr21-screen490-1431.md)

## Opening Constraints

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 30 closed with no canonical retained eval.
- Do not spend the next round on small observation-input damping, path-reversal residue coefficients, regime-selector / split-bus polish, floor-partition coefficient repair, classifier/protection-only controls, aged-premium caps, fee-rent overlays, strict LVR/reserve floors, volume/size/collision lattices, temporal clearing clocks, final quote arbiters, or layer 5/6 opportunity paths.
- Next accepted batch needs at least four critic-approved strategy design improvements before source work starts.
- The proposer/critic loop must iterate until those four accepted designs are distinct in topology, scaffold layer ownership, vocabulary, implementation design, and nonlinearity, with explicit layer ownership, allowed/forbidden consumers, positive expected movement in `mean_edge` or a named problem-space metric, non-no-op expected movement, and kill thresholds tied to `screen_0005`.

## Round 31: External Evidence Interface Batch

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 30 killed path-reversal residue as a near-no-op / slight sub-incumbent observation transform.

### Subagent Workflow

- Topology proposer supplied eight candidates:
  - `PriorTradeMarkoutLedger`
  - `MarginalSlopeDisplacementCodec`
  - `FairValueCorridorProjector`
  - `DirectionEntropyState`
  - `AccelerationBoundedFairUpdate`
  - `SideLabelChecksum`
  - `CalmRebateFirewall`
  - `BandpassDivergenceEncoder`
- Saturation critic accepted four worker probes, deferred one lower-priority idea, and rejected three:
  - Accepted `PriorTradeMarkoutLedger` as the cleanest realized prior-fill markout topology, constrained to last side / last spot / bounded adverse markout and no direct spread, protection, opportunity, refill, recapture, inventory, or final quote access.
  - Accepted `MarginalSlopeDisplacementCodec` only as a raw layer-1 AMM curve-shape codec feeding observation inputs, not as a curvature guard, strict LVR floor, reserve floor, or direct protection rule.
  - Accepted `FairValueCorridorProjector` as a latent-spot-only corridor/deadband projector, not another input damping pass.
  - Accepted `BandpassDivergenceEncoder` as a nonlinear divergence-shape encoder before memory/classifier consumption.
  - Deferred `SideLabelChecksum` as a lower-priority side-risk interface sanity check because the four-design worker floor was already met and side-label sanity checks risked becoming support-only polish.
  - Rejected `DirectionEntropyState` as too close to signed-impact classifier / volume-size-collision / temporal-clearing evidence.
  - Rejected `AccelerationBoundedFairUpdate` as too close to Round 30 path-residue and small observation-input damping.
  - Rejected `CalmRebateFirewall` as support-only shared-rebate / fee-band repair language.
- Enforced entropy constraints:
  - four worker paths before any retained eval decision
  - no layer 5/6 edits
  - no retained-lane mutation
  - no direct shared-spread/protection magnitude edits for upstream codecs
  - no opportunity cuts, refill, recapture, inventory, final quote selection, premium caps, temporal clocks, volume/size/collision lattices, or regime-selector / split-bus polish

### Accepted Probe Contracts

- `PriorTradeMarkoutLedger`
  - Layer mutation: prior-fill outcome observation into bounded layer 2 adverse markout memory.
  - Interface boundary: store last side and last spot, score whether the next observed spot movement made that fill adverse, and feed only `hazardObservation` / at most `divergenceMemory`.
  - Forbidden consumers: direct shared spread, side protection magnitude, opportunity/refill/recapture, inventory, and final quote selection.
  - Kill signature: no activation, `quote_selectivity_ratio > 22`, `time_weighted_mean_fee < 0.00460`, `low_retail_mean_edge < 416.3`, `low_volatility_mean_edge < 464.0`, or failure to beat `screen_0005` unless every floor slice clears.
- `FairValueCorridorProjector`
  - Layer mutation: layer 2 latent fair-value update geometry.
  - Interface boundary: project latent spot through a corridor/deadband around observed spot vs latent spot; downstream memories only observe the resulting gap naturally.
  - Forbidden consumers: direct hazard, shared spread, side protection, opportunity cuts, refill, recapture, inventory, and final quote assembly.
  - Kill signature: Round 30 near-no-op, `quote_selectivity_ratio < 14` or `> 22`, `time_weighted_mean_fee < 0.00460`, floors below Round 30, or failure to beat `screen_0005`.
- `MarginalSlopeDisplacementCodec`
  - Layer mutation: raw layer-1 AMM curve-shape residual into observation inputs.
  - Interface boundary: use a bounded nonlinear displacement residual only for `volObservation`, `hazardObservation`, or `divergenceMemory`.
  - Forbidden consumers: direct shared spread / protection, strict LVR floor, reserve floor, premium cap, and layer 5/6 paths.
  - Kill signature: incumbent-phenotype no-op, `time_weighted_mean_fee > 0.00520`, `low_decile_mean_edge < 370.4`, or failure to beat `screen_0005` without material floor improvement.
- `BandpassDivergenceEncoder`
  - Layer mutation: layer-1 divergence-shape transform before memory/classifier consumption.
  - Interface boundary: triangular / bandpass nonlinear divergence encoding may feed only `divergenceVol`, `hazardObservation`, and `divergenceMemory`.
  - Forbidden consumers: direct floors, fee-rent overlays, clocks, classifier-only protection switches, and opportunity paths.
  - Kill signature: `quote_selectivity_ratio > 22`, `arb_loss_to_retail_gain > 0.10`, `low_decile_mean_edge < 370.4`, or failure to beat `screen_0005` without material floor improvement.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round31/prior_trade_markout_ledger.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round31/fair_value_corridor_projector.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round31/marginal_slope_displacement_codec.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round31/bandpass_divergence_encoder.sol`

### Probe Results

- `PriorTradeMarkoutLedger`
  - Mean edge: `407.38030152095666`
  - Delta vs `screen_0005`: `-79.63206244147529`
  - Key profile: `arb_loss_to_retail_gain=0.2549070488337082`, `quote_selectivity_ratio=70.58838810689362`, `time_weighted_mean_fee=0.003611175374166309`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=361.37180290725763`, `low_volatility_mean_edge=415.08204884182834`
  - Outcome: hard kill as over-open release. Realized prior-fill markout was distinct vocabulary, but feeding it into the same upstream evidence path reopened leakage and collapsed floors.
- `FairValueCorridorProjector`
  - Mean edge: `485.84820131753725`
  - Delta vs `screen_0005`: `-1.1641626448947022`
  - Key profile: `arb_loss_to_retail_gain=0.09956622167646197`, `quote_selectivity_ratio=21.314085786484632`, `time_weighted_mean_fee=0.004671381295631146`
  - Floor slices: `low_decile_mean_edge=370.72086415706656`, `low_retail_mean_edge=415.8076668477263`, `low_volatility_mean_edge=463.19446914795935`
  - Outcome: killed as sub-incumbent latent-state geometry. It avoided collapse but did not create non-no-op improvement over the current frontier.
- `MarginalSlopeDisplacementCodec`
  - Mean edge: `485.9267146331021`
  - Delta vs `screen_0005`: `-1.085649329329843`
  - Key profile: `arb_loss_to_retail_gain=0.09928838506792233`, `quote_selectivity_ratio=21.235426244961666`, `time_weighted_mean_fee=0.004675601229877812`
  - Floor slices: `low_decile_mean_edge=370.7055017340306`, `low_retail_mean_edge=415.8995469515488`, `low_volatility_mean_edge=463.3679010949565`
  - Outcome: killed as near-no-op curve-shape codec. The bounded residual barely moved the incumbent phenotype and did not compensate with floor-slice breakout.
- `BandpassDivergenceEncoder`
  - Mean edge: `486.8594564114263`
  - Delta vs `screen_0005`: `-0.15290755100565`
  - Key profile: `arb_loss_to_retail_gain=0.09800065545458497`, `quote_selectivity_ratio=20.797254541087312`, `time_weighted_mean_fee=0.0047121919511526715`
  - Floor slices: `low_decile_mean_edge=371.3402106217941`, `low_retail_mean_edge=416.6905248976681`, `low_volatility_mean_edge=464.16774791672765`
  - Outcome: best of the batch but still killed below `screen_0005`. The nonlinear bandpass was constructive versus the incumbent profile, but not enough to earn retained eval.

### Decision

- No Round 31 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation and probe commands:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round31/prior_trade_markout_ledger.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round31/prior_trade_markout_ledger.sol > artifacts/scratch_probes/apr21-screen490-1431/round31/prior_trade_markout_ledger.json`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round31/fair_value_corridor_projector.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round31/fair_value_corridor_projector.sol > artifacts/scratch_probes/apr21-screen490-1431/round31/fair_value_corridor_projector.json`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round31/marginal_slope_displacement_codec.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round31/marginal_slope_displacement_codec.sol > artifacts/scratch_probes/apr21-screen490-1431/round31/marginal_slope_displacement_codec.json`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round31/bandpass_divergence_encoder.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round31/bandpass_divergence_encoder.sol > artifacts/scratch_probes/apr21-screen490-1431/round31/bandpass_divergence_encoder.json`

### Updated Entropy Discipline

- Public microstructure / AMM evidence is not sufficient novelty by itself. Round 31 showed that prior-fill markout can still become a hidden release path if it feeds the same upstream hazard/divergence consumers without a protection-preserving boundary.
- Retire standalone layer 1/2 codec probes whose only claim is better observation geometry. Fair-value corridor, marginal-slope residual, and bandpass divergence all avoided catastrophic overcharge, but stayed below `screen_0005`; a future codec must be paired with a different primary anchor or prove a materially different floor-risk owner before source work.
- `BandpassDivergenceEncoder` is the only Round 31 scratch result worth keeping as a diagnostic reference: it improved floor slices versus the incumbent while missing best raw by `0.153`, so it may inform later combinations but should not receive local coefficient polish.
- Round 32 should not spend another worker set on hazard/divergence input reshaping. Prefer a topology that changes the allocation of protection versus benign capture without routing through the same `hazardObservation` / `divergenceMemory` path, and still keep layer 5/6 opportunity paths closed unless a stronger primary owner exists.
