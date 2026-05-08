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

## Round 23: Public Microstructure Fee-Rent Probe Closure

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 22 killed estimator trust / reconstructability / quorum gates as severe over-open floor collapses.

### Entropy And Outside-Evidence Screen

- External microstructure / AMM guidance was used only at the abstraction level:
  - bid-ask spreads are commonly decomposed into adverse-selection, inventory, and order-processing components
  - AMM LP losses can be framed as adverse-selection / loss-versus-rebalancing costs from stale pool prices
  - dynamic AMM fee work treats optimal fees as a function of volatility and trading volume
- The accepted search shape was intentionally protection-preserving:
  - zero layer 5/6 opportunity, refill, recapture, or inventory-overlay edits
  - no estimator confidence gate that can open quotes broadly
  - no split-bus or regime-selector coefficient polish
  - nonlinearities had to add or preserve rent under uncertainty, not lower protection

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round23/`
- Families explored:
  - `volatility_indexed_base_spread.sol`
  - `inventory_direction_fee_slope.sol`
  - `two_clock_risk_rent.sol`

### Probe Results

- `VolatilityIndexedBaseSpread`
  - Mean edge: `471.4090265460181`
  - Delta vs `screen_0005`: `-15.60333741641386`
  - Key profile: `arb_loss_to_retail_gain=0.10547537476956846`, `quote_selectivity_ratio=19.956456995942574`, `time_weighted_mean_fee=0.005285275577273715`
  - Floor slices: `low_decile_mean_edge=302.404585455161`, `low_retail_mean_edge=396.81958069626876`, `low_volatility_mean_edge=461.3928150072657`
  - Outcome: least bad of the round but still a clear discard; the shared volatility rent preserved selectivity better than the other two probes but overcharged / undercaptured enough to damage mean edge and floors.
- `InventoryDirectionFeeSlope`
  - Mean edge: `448.0390342527364`
  - Delta vs `screen_0005`: `-38.97332970969556`
  - Key profile: `arb_loss_to_retail_gain=0.16952932849048355`, `quote_selectivity_ratio=38.750156491056096`, `time_weighted_mean_fee=0.004374932744584207`
  - Floor slices: `low_decile_mean_edge=263.29772182291515`, `low_retail_mean_edge=398.9626689873656`, `low_volatility_mean_edge=415.80695986683446`
  - Outcome: killed; inventory-direction surcharge behaved like another over-open asymmetric-fee basin and collapsed low-decile / low-volatility slices.
- `TwoClockRiskRent`
  - Mean edge: `407.19688460105135`
  - Delta vs `screen_0005`: `-79.8154793613806`
  - Key profile: `arb_loss_to_retail_gain=0.24297943890923182`, `quote_selectivity_ratio=58.254023609728236`, `time_weighted_mean_fee=0.004171032726203912`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=361.25767912260324`, `low_volatility_mean_edge=415.001729228952`
  - Outcome: killed; dual-clock rent replayed the Round 21-22 over-open/floor-collapse basin.

### Decision

- No Round 23 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation passed for all three scratch sources:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round23/volatility_indexed_base_spread.sol`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round23/inventory_direction_fee_slope.sol`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round23/two_clock_risk_rent.sol`

### Updated Entropy Discipline

- Retire fee-rent probes that only add a global or asymmetric surcharge after the incumbent has already produced its shared spread / side protection.
- Round 24 may test one narrower AMM-specific floor proxy only if it is a layer-4 floor component with strict forbidden consumers and no release path.
- Keep the batch distribution upstream / mid-scaffold:
  - two candidates in layers 1-3 or one layer-4 floor proxy at most
  - zero layer 5/6
  - no estimator trust gate, split-bus polish, regime-selector polish, final-quote arbiter, or opportunity admission

## Round 24: LVR Floor Proxy Worker Probe

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Round 23 retired post-spread fee-rent overlays that added global or asymmetric rent after the incumbent spread / protection path had already run.

### Subagent Workflow

- Topology proposer supplied three high-entropy contracts:
  - `FrequentBatchClearingBand`
  - `ConstantProductCurvatureFloor`
  - `RetailAuctionReserveBand`
- Saturation critic enforced:
  - zero layer 5/6
  - no split-bus or regime-selector polish
  - no estimator trust gates that attenuate protection
  - no final-quote arbiter or downstream service admission
  - nonlinearities must preserve or add protection under uncertainty
- Strategy worker owned a single accepted scratch implementation:
  - `LVRProxySpreadFloor`
  - owned files only under `artifacts/scratch_probes/apr21-screen490-1431/round24/`

### Accepted Probe Contract

- `LVRProxySpreadFloor`
  - Layer mutation: narrow layer 4 shared-spread floor proxy.
  - Interface boundary: use observed mark movement versus latent fair estimate / divergence as a loss-versus-rebalancing proxy; it may only add or preserve a bounded shared-spread floor.
  - Forbidden consumers: estimator selection, final quote arbiter, side protection formulas, inventory overlay, calm boosts, recapture/refill/opportunity, and all layer 5/6 branches.
  - Expected movement: preserve selectivity and floors while testing whether an AMM-specific protection floor can improve over incumbent without the Round 23 global-rent failure.
  - Kill signature: exact no-op, floor damage, selectivity above the incumbent band, or failure to beat `screen_0005`.

### Probe Source

- `artifacts/scratch_probes/apr21-screen490-1431/round24/lvr_proxy_spread_floor.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round24/lvr_proxy_spread_floor.json`

### Probe Result

- `LVRProxySpreadFloor`
  - Mean edge: `485.9238751592638`
  - Delta vs incumbent: `+0.00010445559197`
  - Delta vs `screen_0005`: `-1.08848880316814`
  - Key profile: `arb_loss_to_retail_gain=0.09961754551074273`, `quote_selectivity_ratio=21.36689716404271`, `time_weighted_mean_fee=0.004662237326549413`
  - Floor slices: `low_decile_mean_edge=370.69883147282303`, `low_retail_mean_edge=415.91377689191506`, `low_volatility_mean_edge=463.3211594973549`
  - Outcome: diagnostic no-op / clear discard; the strict LVR proxy avoided Round 23's over-open collapse, but it did not move beyond the incumbent phenotype and remained well below the retained best raw branch.

### Decision

- No Round 24 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation and probe commands:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round24/lvr_proxy_spread_floor.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round24/lvr_proxy_spread_floor.sol > artifacts/scratch_probes/apr21-screen490-1431/round24/lvr_proxy_spread_floor.json`

### Updated Entropy Discipline

- Strict protection-preserving LVR floor proxies are safer than global fee-rent overlays but currently too no-op to spend.
- Do not turn Round 25 into coefficient tuning on `LVRProxySpreadFloor`.
- Next work should move to a different primary interface:
  - layer 1/3 batch-clearing or latency-arbitrage pressure classification with no release path
  - layer 1/4 constant-product curvature floor tied to curve-depth stress
  - layer 2/3 reserve-band classification that protects low-retail / low-decile floors before shared spread assembly

## Round 25: Curvature Guard And Protection-Starvation Closure

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 24 killed strict LVR floor tuning as a near-exact no-op and required a different primary interface for the next batch.

### Subagent Workflow

- Topology proposer supplied three high-entropy contracts:
  - `BatchClearingLatencyPressure`
  - `ConstantProductCurvatureGuard`
  - `ReserveBandExhaustionClassifier`
- Saturation critic enforced:
  - at least two probes in layers 1-3 and at most one layer-4 probe
  - zero layer 5/6 edits
  - no final quote arbiter, release path, global fee-rent overlay, LVR floor tuning, estimator trust gate, split-bus polish, or regime-selector polish
  - explicit allowed/forbidden consumers and falsifiable kill signatures before source work
- Strategy worker owned scratch-only source and result files under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round25/`

### Accepted Probe Contracts

- `BatchClearingLatencyPressure`
  - Layer mutation: layer 1 observation into layer 3 classifier.
  - Interface boundary: classify latency-arbitrage pressure from time gap, spot jump, trade size, and same-direction flow clustering.
  - Allowed consumers: `hazardObservation`, `eventSignal`, and pre-shared-spread protection only.
  - Forbidden consumers: estimator selection, latent-spot trust, side opportunity cuts, passive recapture/refill, inventory centering, final fee assembly, and all release paths.
  - Kill signature: selectivity blowout, low-decile collapse, protection starvation, or failure to beat `screen_0005`.
- `ConstantProductCurvatureGuard`
  - Layer mutation: layer 1 curve-depth geometry into a narrow layer 4 shared-spread floor.
  - Interface boundary: use immediate constant-product curve stress from trade size and reserve geometry; it may only add a bounded `sharedSpread` component.
  - Forbidden consumers: hazard/calm/latent-state updates, side-specific protection, inventory, recapture/refill/opportunity, and final quote arbitration.
  - Kill signature: exact LVR-floor no-op, fee lift without floor improvement, over-tightening, or failure to beat `screen_0005`.
- `ReserveBandExhaustionClassifier`
  - Layer mutation: layer 2 reserve-depth state into layer 3 protection classifier.
  - Interface boundary: export bounded reserve exhaustion as curve fragility evidence for protection only.
  - Forbidden consumers: estimator confidence, calm/recenter logic, passive recapture/refill, safe-side opportunity, inventory overlay, split-bus/regime-selector paths, and final quote selection.
  - Kill signature: inventory-direction fee-slope replay, selectivity above `24`, low-retail / low-decile damage, protection starvation, or failure to beat `screen_0005`.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round25/batch_clearing_latency_pressure.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round25/constant_product_curvature_guard.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round25/reserve_band_exhaustion_classifier.sol`

### Probe Results

- `BatchClearingLatencyPressure`
  - Mean edge: `247.97966378761004`
  - Delta vs incumbent: `-237.9441069160618`
  - Delta vs `screen_0005`: `-239.0327001748219`
  - Key profile: `arb_loss_to_retail_gain=0.12337673354812174`, `quote_selectivity_ratio=3.8545553535765498`, `time_weighted_mean_fee=0.03200803263433315`
  - Floor slices: `low_decile_mean_edge=168.48586026147126`, `low_retail_mean_edge=212.41608899233034`, `low_volatility_mean_edge=235.6342054653155`
  - Outcome: killed; the batch-clearing pressure classifier was not over-open, but it starved the strategy with excessive protection and collapsed all tracked floors.
- `ConstantProductCurvatureGuard`
  - Mean edge: `486.40855889392367`
  - Delta vs incumbent: `+0.48478819025184`
  - Delta vs `screen_0005`: `-0.60380506850828`
  - Key profile: `arb_loss_to_retail_gain=0.09564675510655068`, `quote_selectivity_ratio=20.201016949018097`, `time_weighted_mean_fee=0.004734749510281449`
  - Floor slices: `low_decile_mean_edge=371.1512446206268`, `low_retail_mean_edge=416.49215644390455`, `low_volatility_mean_edge=463.6827563164905`
  - Outcome: positive scratch anchor versus the incumbent and all floor slices, but still below `screen_0005` and the breakout target; do not run canonically unless paired with a structurally different primary interface or a stronger curvature-specific follow-up.
- `ReserveBandExhaustionClassifier`
  - Mean edge: `350.1360101174001`
  - Delta vs incumbent: `-135.78776058627174`
  - Delta vs `screen_0005`: `-136.87635384503185`
  - Key profile: `arb_loss_to_retail_gain=0.10419499412982781`, `quote_selectivity_ratio=6.472105510218651`, `time_weighted_mean_fee=0.01609908768720115`
  - Floor slices: `low_decile_mean_edge=253.69190091754814`, `low_retail_mean_edge=296.63399740662936`, `low_volatility_mean_edge=334.83136861525406`
  - Outcome: killed; reserve-band exhaustion behaved like another over-tight protection-starvation basin rather than a usable classifier.

### Decision

- No Round 25 candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation passed for all three scratch sources:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round25/batch_clearing_latency_pressure.sol`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round25/constant_product_curvature_guard.sol`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round25/reserve_band_exhaustion_classifier.sol`

### Updated Entropy Discipline

- Treat `ConstantProductCurvatureGuard` as a real but sub-best scratch anchor. It is useful as curve-geometry evidence, not as a standalone retained candidate.
- Retire broad batch-clearing latency pressure and reserve-band exhaustion classifiers that push protection high enough to starve retail capture.
- Round 26 should start a new chunk and avoid simply retuning curvature coefficients. A valid next batch needs a different primary interface, with curvature allowed only as a bounded secondary adjunct if the primary idea owns distinct evidence.
