# apr21-screen490-1431 rounds 21-25

Run index: [apr21-screen490-1431.md](apr21-screen490-1431.md)

## Round 21: Forecast Ownership And Quote-Arbiter Search

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Gap to breakout target: `2.98763603756805`.

### Subagent Entropy Screen

- Topology proposer supplied three structurally distinct contracts:
  - `ForecastErrorOwnershipBus`: layer 2 latent-estimator ownership via bounded forecast-error classification.
  - `LexicographicDualQuoteArbiter`: layer 4 final quote assembly with a floor-risk-first arbiter.
  - `CapacityLimitedServiceWindow`: the only layer 6 slot, using finite safe-side service capacity admitted by a leakage band.
- Saturation critic rejected another round of:
  - split-bus local variants
  - regime-selector floor/fee polish
  - support-control stacking
  - scalar hazard dampers
  - layer 5/6 exploit batches
  - broad fee-band rewrites

### Accepted Probe Contracts

- `ForecastErrorOwnershipBus`
  - Layer mutation: layer 2 latent estimator ownership.
  - Interface boundary: export only a bounded forecast-error class from prior latent prediction vs realized spot; allow it into estimator/observation attenuation only.
  - Forbidden consumers: shared spread, side protection, opportunity, calm/recenter/refill, inventory, burst, or fee-floor formulas.
  - Expected movement: preserve `screen_0005` floor lift while lowering leakage/selectivity.
  - Kill signature: exact no-op, worse low-decile, or broad over-open fee compression.
- `LexicographicDualQuoteArbiter`
  - Layer mutation: layer 4 final quote assembly topology.
  - Interface boundary: compute candidate quotes from existing public signals and apply a bounded final quote arbiter; do not change latent state, observation basis, classifier, shared-spread internals, side protection, recapture, or opportunity formulas.
  - Expected movement: reduce hidden coupling where mean-edge gains reopen leakage, while keeping fees near the `screen_0005` band.
  - Kill signature: broad fee retune, higher jumpiness, floor damage, or replay of near-incumbent quote assembly.
- `CapacityLimitedServiceWindow`
  - Layer mutation: layer 6 safe-side service admission, used as the only downstream exploit slot.
  - Interface boundary: safe-side opportunity cut is bounded by finite capacity admitted only under strict leakage-band evidence.
  - Forbidden consumers: hazard/calm classification, estimator selection, shared spread, side protection magnitude, inventory, burst admission, and refill.
  - Expected movement: recover benign capture without repeating `regime_selector_mild_fee_release` over-open failure.
  - Kill signature: selectivity above `21`, low-decile below `371`, low-retail damage, or mean-edge loss from over-constraining service.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round21/`
- Families explored:
  - `forecast_error_observation_gate.sol`
  - `final_quote_floor_arbiter.sol`
  - `capacity_service_window.sol`

### Probe Results

- `ForecastErrorObservationGate`
  - Mean edge: `445.69449323988164`
  - Delta vs `screen_0005`: `-41.31787072255031`
  - Key profile: `arb_loss_to_retail_gain=0.1742855948004657`, `quote_selectivity_ratio=39.98002168225488`, `time_weighted_mean_fee=0.004359317165598795`
  - Floor slices: `low_decile_mean_edge=263.3092323815264`, `low_retail_mean_edge=398.5204150717049`, `low_volatility_mean_edge=415.55585121409496`
  - Outcome: killed; forecast-error gating over-opened, sharply worsened leakage/selectivity, and collapsed floors.
- `FinalQuoteFloorArbiter`
  - Mean edge: `474.6530587735876`
  - Delta vs `screen_0005`: `-12.35930518884435`
  - Key profile: `arb_loss_to_retail_gain=0.11673447703887839`, `quote_selectivity_ratio=24.847005546098423`, `time_weighted_mean_fee=0.004698130598566575`
  - Floor slices: `low_decile_mean_edge=304.5757016194667`, `low_retail_mean_edge=399.2405869300657`, `low_volatility_mean_edge=464.4936465100409`
  - Outcome: least bad of the round, but still a clear discard; low-volatility improved slightly while low-decile, low-retail, leakage, and selectivity failed badly.
- `CapacityServiceWindow`
  - Mean edge: `466.7498534407737`
  - Delta vs `screen_0005`: `-20.26251052165824`
  - Key profile: `arb_loss_to_retail_gain=0.11756259168662793`, `quote_selectivity_ratio=22.804441148858096`, `time_weighted_mean_fee=0.005155249844502974`
  - Floor slices: `low_decile_mean_edge=300.83338670613875`, `low_retail_mean_edge=392.3911047931943`, `low_volatility_mean_edge=455.83808608637406`
  - Outcome: killed; finite service admission behaved like an over-constrained downstream slot and damaged all tracked floors.

### Decision

- No Round 21 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- The three-role subagent workflow was used:
  - topology proposer supplied forecast-error, dual-quote, and capacity-window contracts
  - entropy critic rejected local split-bus/regime-selector/support-control polishing
  - strategy worker implemented scratch-only variants and stopped after all three hit floor-collapse signatures

### Updated Entropy Discipline

- Retire Round 21's broad quote-arbiter/service-window attempts unless a future probe can model downside floor risk upstream instead of applying downstream admission.
- Do not tune `ForecastErrorObservationGate`; the first implementation was not merely weak but a strong over-open leak.
- Round 22 should leave layer 6 alone and focus on a different upstream/mid-scaffold ownership model. Good candidates should be layer 1-3 or narrowly layer 4, with no safe-side opportunity edits.

## Round 22: Upstream Reconstructability And Quorum Probes

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 21 killed downstream quote arbitration and layer 6 service admission because both collapsed floors.

### Subagent Entropy Screen

- Topology proposer supplied three upstream/mid-scaffold contracts:
  - `ImpactReconstructabilityEncoder`
  - `HorizonQuorumStateContract`
  - `AdverseOptionalityClassifier`
- Saturation critic accepted only layer 1-3 or narrow layer 4 work and rejected:
  - layer 5/6 safe-side opportunity
  - final-quote-only arbitration
  - support-control stacking
  - `screen_0005` coefficient polish
  - split-bus side-only polish

### Accepted Probe Contracts

- `ImpactReconstructabilityEncoder`
  - Layer mutation: layer 1 observation partition into layer 2 state ownership.
  - Interface boundary: classify whether price movement is explainable by contemporaneous trade size/participation.
  - Forbidden consumers: shared spread magnitude, side protection, quote assembly, burst, recapture/refill/opportunity, inventory.
- `HorizonQuorumStateContract`
  - Layer mutation: layer 2 latent-state interface.
  - Interface boundary: compare short/medium/long estimator agreement and export a bounded quorum state for latent estimate and classifier confidence only.
  - Forbidden consumers: direct spread, final quote, side opportunity, layer 5/6, inventory, refill, recentering, regime-selector coefficient polish.
- `AdverseOptionalityClassifier`
  - Layer mutation: layer 3 classifier with narrow layer 4 pre-quote width budgeting.
  - Interface boundary: classify stale-quote optionality from quote-age, directional fill pressure, and mark movement.
  - Forbidden consumers: final quote arbiter, safe-side service, recapture/refill/opportunity, inventory, burst, split-bus/regime-selector coefficient polish.

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round22/`
- Families explored:
  - `impact_reconstructability_encoder.sol`
  - `horizon_quorum_state_contract.sol`
  - `adverse_optionality_classifier.sol`

### Probe Results

- `ImpactReconstructabilityEncoder`
  - Mean edge: `408.131`
  - Key profile: `arb_loss_to_retail_gain=0.2506`, `quote_selectivity_ratio=66.94`
  - Floor slices: `low_decile_mean_edge=213.535`, `low_retail_mean_edge=362.081`, `low_volatility_mean_edge=415.807`
  - Outcome: killed; severe over-open/floor-collapse replay.
- `HorizonQuorumStateContract`
  - Mean edge: `419.570`
  - Key profile: `arb_loss_to_retail_gain=0.2328`, `quote_selectivity_ratio=61.68`
  - Floor slices: `low_decile_mean_edge=224.566`, `low_retail_mean_edge=373.641`, `low_volatility_mean_edge=413.798`
  - Outcome: killed; quorum gating behaved like the Round 21 forecast-error basin rather than a controlled estimator interface.
- `AdverseOptionalityClassifier`
  - Mean edge: `443.241`
  - Key profile: `arb_loss_to_retail_gain=0.1568`, `quote_selectivity_ratio=29.36`
  - Floor slices: `low_decile_mean_edge=262.908`, `low_retail_mean_edge=395.662`, `low_volatility_mean_edge=413.498`
  - Outcome: best by mean edge but still a clear discard; widened pre-quote budgeting did not stop arb leakage and crushed floors.

### Decision

- No Round 22 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`

### Updated Entropy Discipline

- Retire estimator-quorum, reconstructability, and stale-quote optionality as implemented; all three were not close misses but severe floor collapses.
- Two consecutive high-entropy batches still fell into over-open/floor-collapse. Round 23 should import outside microstructure/AMM guidance and avoid internal relabeling.
- Candidate shape should be a simpler robust fee/regime boundary or inventory/external-price-inspired control at the abstraction level only, without inspecting oracle/reference code and without broad fee compression.
