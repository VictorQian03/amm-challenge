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

## Round 32: Allocation-Owner Interface Batch

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 31 killed standalone public-evidence / AMM geometry imports unless they introduce a protection-preserving owner rather than another observation codec.

### Subagent Workflow

- Topology proposer supplied eight candidates:
  - `RetailSurplusConservationAccount`
  - `BenignFlowCapacityMeter`
  - `ProtectionBudgetEscrowSplit`
  - `ToxicityCostInventorySeparation`
  - `FragileStateReadOnlyFirewall`
  - `CrossSideSymmetryDebt`
  - `SelectiveContinuityGate`
  - `TwoAccountSpreadAssembly`
- Saturation critic accepted five worker probes and rejected or deferred three:
  - Accepted `RetailSurplusConservationAccount` as a layer 2 retail surplus / deficit account that could only preserve incumbent shared-spread protection when surplus was negative.
  - Accepted `BenignFlowCapacityMeter` as a non-size / non-volume benign capacity class with layer 4 allocation authority.
  - Accepted `ToxicityCostInventorySeparation` as the public-evidence motivated layer 2 separation between adverse-selection cost and inventory / capital-cost evidence.
  - Accepted `CrossSideSymmetryDebt` as a layer 2 bid / ask treatment-imbalance account consumed only by shared-width allocation.
  - Accepted `TwoAccountSpreadAssembly` as the clearest layer 4 split between adverse-protection width and benign-service width.
  - Rejected `ProtectionBudgetEscrowSplit` as same-spine with `TwoAccountSpreadAssembly`.
  - Rejected `FragileStateReadOnlyFirewall` as support-only protection blocking with weak expected movement and high no-op risk.
  - Deferred `SelectiveContinuityGate` because continuity / evidence-retention language was too close to Round 28 release and Round 29 overprotection without a sharper anti-release owner.
- Enforced entropy constraints:
  - five worker paths before any retained eval decision
  - no layer 5/6 opportunity, refill, recapture, inventory, or final quote paths
  - no retained-lane mutation
  - no regime-selector / split-bus polish
  - no direct hazard/divergence input reshaping, temporal clearing, fee-rent overlays, strict LVR/reserve floors, volume/size/collision lattices, or weak support stacks

### Accepted Probe Contracts

- `RetailSurplusConservationAccount`
  - Layer mutation: layer 2 retail surplus / deficit accounting state with layer 3 floor-risk labeling.
  - Interface boundary: layer 4 could preserve incumbent shared-spread floor only when surplus was negative.
  - Forbidden consumers: layer 5/6, opportunity, recapture/refill, inventory, final quote, direct fee compression/release, regime/split-bus paths, and floor-slice conditionals.
  - Kill signature: broad fee release, `quote_selectivity_ratio` outside `16-22`, `time_weighted_mean_fee < 0.00470`, `low_retail_mean_edge < 416.88`, `low_volatility_mean_edge < 464.15`, or failure to beat `screen_0005` without material floor lift.
- `BenignFlowCapacityMeter`
  - Layer mutation: layer 1 -> 2 benign-capacity class from non-size / non-volume evidence.
  - Interface boundary: layer 4 could reallocate unchanged incumbent spread across capacity classes; layer 3 could suppress overprotection only in the highest-capacity state.
  - Forbidden consumers: direct hazard/divergence rewrites, side-protection magnitude, layer 5/6, final quote, opportunity, and volume/size/collision buckets.
  - Kill signature: `quote_selectivity_ratio > 24`, `time_weighted_mean_fee < 0.00460`, `low_retail_mean_edge < 416.3`, no-op phenotype, or low-decile giveback without mean gain.
- `ToxicityCostInventorySeparation`
  - Layer mutation: public microstructure-motivated layer 2 separation of adverse-selection cost evidence from capital / inventory-cost evidence.
  - Interface boundary: layer 3 could classify adverse-selection-only states; layer 4 could preserve incumbent spread only when adverse-selection cost dominated.
  - Forbidden consumers: actual inventory overlay, layer 5/6, fee-rent surcharge, prior-fill markout, hazard/divergence reshaping, and final quote.
  - Kill signature: `time_weighted_mean_fee > 0.00520`, `quote_selectivity_ratio > 24`, floors falling together, no movement, or post-spread fee-rent-like profile.
- `CrossSideSymmetryDebt`
  - Layer mutation: layer 2 bid / ask symmetry-debt accumulator.
  - Interface boundary: layer 4 could rebalance only symmetric / shared width; layer 3 could observe debt class for attribution.
  - Forbidden consumers: side-specific opportunity, inventory, final quote, side-protection magnitude, split-bus polish, and classifier-local hazard controls.
  - Kill signature: split-bus-like phenotype, `quote_selectivity_ratio > 24`, `low_decile_mean_edge < 371.0`, `low_retail_mean_edge < 416.3`, `time_weighted_mean_fee < 0.00460`, or no leakage improvement.
- `TwoAccountSpreadAssembly`
  - Layer mutation: layer 4 quote-width assembly with non-fungible adverse-protection and benign-service accounts.
  - Interface boundary: layer 3 could choose account mix from existing state classes; only layer 4 quote-width calculation could consume the accounts.
  - Forbidden consumers: layer 5/6, fee-rent overlays, final quote, opportunity/refill/recapture, strict floor proxies, and weak support stacking.
  - Kill signature: broad fee compression, fee spike with floor collapse, `quote_selectivity_ratio > 24`, fee outside `0.00470-0.00510`, or failure to beat `screen_0005`.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round32/retail_surplus_conservation_account.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round32/benign_flow_capacity_meter.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round32/toxicity_cost_inventory_separation.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round32/cross_side_symmetry_debt.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round32/two_account_spread_assembly.sol`

### Probe Results

- `RetailSurplusConservationAccount`
  - Mean edge: `421.1069584329718`
  - Delta vs `screen_0005`: `-65.90540552946014`
  - Key profile: `arb_loss_to_retail_gain=0.22603676268881023`, `quote_selectivity_ratio=57.72528147394887`, `time_weighted_mean_fee=0.003915732533774123`
  - Floor slices: `low_decile_mean_edge=226.13453416667554`, `low_retail_mean_edge=375.32809114069516`, `low_volatility_mean_edge=415.0820488418958`
  - Outcome: hard kill as over-open release. The retail surplus account lowered fees and reopened leakage rather than preserving the shared-spread floor.
- `BenignFlowCapacityMeter`
  - Mean edge: `485.92377070367183`
  - Delta vs `screen_0005`: `-1.0885932587601133`
  - Key profile: `arb_loss_to_retail_gain=0.09961822784430861`, `quote_selectivity_ratio=21.366983876018754`, `time_weighted_mean_fee=0.004662250340166877`
  - Floor slices: `low_decile_mean_edge=370.69865470550553`, `low_retail_mean_edge=415.9137203431734`, `low_volatility_mean_edge=463.32099611706855`
  - Outcome: killed as baseline-like no-op / weak release. It did not create a new benign-capacity owner strong enough to move away from the incumbent phenotype.
- `ToxicityCostInventorySeparation`
  - Mean edge: `406.6416428677225`
  - Delta vs `screen_0005`: `-80.37072109470944`
  - Key profile: `arb_loss_to_retail_gain=0.25765675564366786`, `quote_selectivity_ratio=72.61554469132757`, `time_weighted_mean_fee=0.003548231397821349`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=360.740084111293`, `low_volatility_mean_edge=414.29749761454696`
  - Outcome: hard kill as over-open release. The public-evidence separation still collapsed into broad fee release when translated into allocation authority.
- `CrossSideSymmetryDebt`
  - Mean edge: `407.3803014679076`
  - Delta vs `screen_0005`: `-79.63206249452435`
  - Key profile: `arb_loss_to_retail_gain=0.25490704886796944`, `quote_selectivity_ratio=70.58838813138075`, `time_weighted_mean_fee=0.003611175373398958`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=361.37180275293304`, `low_volatility_mean_edge=415.08204884182834`
  - Outcome: hard kill as over-open release / split-bus-like relapse. Symmetry-debt allocation behaved like another broad release path rather than leakage containment.
- `TwoAccountSpreadAssembly`
  - Mean edge: `472.9831292462716`
  - Delta vs `screen_0005`: `-14.029234716160374`
  - Key profile: `arb_loss_to_retail_gain=0.12673885314564784`, `quote_selectivity_ratio=28.19034965540809`, `time_weighted_mean_fee=0.004495824092105009`
  - Floor slices: `low_decile_mean_edge=362.4036831613388`, `low_retail_mean_edge=404.88800471555095`, `low_volatility_mean_edge=450.10712593053523`
  - Outcome: killed as partial retail lift with leakage/floor damage. Retail edge improved, but arb leakage, selectivity, and all tracked floor slices failed.

### Decision

- No Round 32 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0005`
- Validation and probe commands:
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round32/retail_surplus_conservation_account.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round32/retail_surplus_conservation_account.sol > artifacts/scratch_probes/apr21-screen490-1431/round32/retail_surplus_conservation_account.json`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round32/benign_flow_capacity_meter.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round32/benign_flow_capacity_meter.sol > artifacts/scratch_probes/apr21-screen490-1431/round32/benign_flow_capacity_meter.json`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round32/toxicity_cost_inventory_separation.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round32/toxicity_cost_inventory_separation.sol > artifacts/scratch_probes/apr21-screen490-1431/round32/toxicity_cost_inventory_separation.json`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round32/cross_side_symmetry_debt.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round32/cross_side_symmetry_debt.sol > artifacts/scratch_probes/apr21-screen490-1431/round32/cross_side_symmetry_debt.json`
  - `uv run amm-match validate artifacts/scratch_probes/apr21-screen490-1431/round32/two_account_spread_assembly.sol`
  - `uv run amm-match hill-climb probe --stage screen --json artifacts/scratch_probes/apr21-screen490-1431/round32/two_account_spread_assembly.sol > artifacts/scratch_probes/apr21-screen490-1431/round32/two_account_spread_assembly.json`

### Updated Entropy Discipline

- Allocation-owner vocabulary is not sufficient novelty when the implementation still gives layer 4 authority to release broad fee width. Retail surplus, adverse-selection/inventory separation, cross-side symmetry debt, and two-account spread assembly all reopened leakage or damaged floors.
- Retire whole-batch attempts whose primary action is reallocating existing layer 4 width unless the proposal includes a hard mechanical floor-preservation invariant before any fee release path. This is a distinct failure from upstream geometry-codec plateau: the ideas moved, but moved through broad fee release.
- `BenignFlowCapacityMeter` is a no-op / baseline-like diagnostic only. It should not receive coefficient polish unless paired with a genuinely new primary owner that changes floor protection without lowering the fee band.
- Round 33 should avoid both standalone observation codecs and standalone layer 4 allocation ledgers. Prefer a new primary owner that can prove protection-vs-benign-capture separation before it reaches shared spread, and keep release/opportunity paths closed.

## Round 33: One-Way Evidence Boundary Batch

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard entering the round: `screen_0005` / `regime-selector-stronger-floor` at `487.01236396243195`.
- Breakout target: `490`.
- Round 32 killed standalone allocation-owner / account-separation vocabulary unless the interface contains a hard floor-preservation invariant before any shared-spread compression.

### Subagent Workflow

- Topology proposer supplied ten candidates:
  - `MonotoneEvidenceFirewall`
  - `AdverseBenignNonSubstitutionContract`
  - `LatentUpdateCircuitBreaker`
  - `RestorationOnlyBenignCertificate`
  - `AsymmetricLossAttributionMatrix`
  - `ProtectionDebtRepaymentGate`
  - `ConvexAdverseEnvelope`
  - `CounterfactualFillRegretBound`
  - `NoDiscountRiskCertificate`
  - `PiecewiseExposureSaturationSurface`
- Saturation critic accepted or narrowed six worker contracts:
  - Accepted `MonotoneEvidenceFirewall` as a layer-2 one-way evidence boundary that can raise or preserve hazard / side-risk evidence but cannot authorize rebates, cuts, refill, recapture, inventory, final quote, or layer-4 release.
  - Accepted `AdverseBenignNonSubstitutionContract` as a layer-3 token separation where adverse evidence may add spread/protection but benign evidence cannot substitute for adverse evidence or feed fee cuts.
  - Accepted `ProtectionDebtRepaymentGate` as a layer-3 debt-before-repair invariant.
  - Accepted `ConvexAdverseEnvelope` as a layer-3 convex adverse-state envelope over volatility, flow pressure, and latent gap.
  - Accepted `CounterfactualFillRegretBound` as an outside-vocabulary layer-2 outcome-memory idea consumed only as side-specific protection.
  - Accepted `PiecewiseExposureSaturationSurface` as a dead-zone plus convex-tail side-protection translator.
- Critic rejected four:
  - Rejected `LatentUpdateCircuitBreaker` as too close to latent geometry / no-op damping.
  - Rejected `RestorationOnlyBenignCertificate` as quiet-recenter / passive-recapture replay risk.
  - Rejected `AsymmetricLossAttributionMatrix` as classifier/protection-only control.
  - Rejected `NoDiscountRiskCertificate` as support-only veto.
- Enforced entropy constraints:
  - six accepted scratch paths before retained decision
  - no standalone observation-codec batch
  - no standalone layer-4 allocation ledger
  - no regime-selector / split-bus polish
  - no floor-partition coefficient repair
  - no layer 5/6 opportunity, refill, recapture, inventory, or final quote edits
  - no retained-lane mutation before a scratch source beat `screen_0005`

### Accepted Probe Contracts

- `MonotoneEvidenceFirewall`
  - Layer mutation: layer 2 boundary validator into layer 3 side-risk evidence.
  - Interface boundary: upstream stress can only raise or preserve `hazardObservation`, `sideHazard`, and side risk.
  - Forbidden consumers: shared rebate, opportunity cuts, refill, recapture, inventory, final quote, and layer-4 width release.
  - Kill signature: `quote_selectivity_ratio > 22`, `time_weighted_mean_fee < 0.00470`, any tracked floor slice below `screen_0005`, or no movement versus incumbent.
- `AdverseBenignNonSubstitutionContract`
  - Layer mutation: layer 3 evidence-token separation.
  - Interface boundary: adverse token may add shared spread and side protection; benign token may only restrict a calm rebate.
  - Forbidden consumers: direct fee compression, opportunity cuts, refill, recapture, inventory, and final quote.
  - Kill signature: `quote_selectivity_ratio > 24`, `time_weighted_mean_fee < 0.00470`, low-retail below `416.8`, low-volatility below `464.1`, or benign evidence behaving like release.
- `ProtectionDebtRepaymentGate`
  - Layer mutation: layer 3 protection debt with debt-before-repair precedence.
  - Interface boundary: debt can raise/hold side protection and veto latent repair; it cannot reduce shared spread or increase opportunity cuts.
  - Forbidden consumers: layer 5/6, refill, recapture, inventory, final quote, and layer-4 release.
  - Kill signature: mean edge below incumbent, `time_weighted_mean_fee > 0.00520` with floor decline, `quote_selectivity_ratio > 24`, or all floors falling together.
- `ConvexAdverseEnvelope`
  - Layer mutation: layer 3 convex adverse envelope.
  - Interface boundary: bounded envelope may add shared spread and side protection.
  - Forbidden consumers: fee rebate, opportunity, refill, recapture, inventory, final quote, temporal clocks, and volume/size lattices.
  - Kill signature: `time_weighted_mean_fee > 0.00520`, `quote_selectivity_ratio < 14` or `> 24`, low-decile below `371`, or no clear arb-loss improvement.
- `CounterfactualFillRegretBound`
  - Layer mutation: layer 2 outcome memory outside incumbent vocabulary.
  - Interface boundary: bounded prior-fill regret may raise side-specific protection only.
  - Forbidden consumers: hazard release, shared spread release, opportunity, refill, recapture, inventory, and final quote.
  - Kill signature: Round 31 prior-markout replay, `quote_selectivity_ratio > 30`, `time_weighted_mean_fee < 0.00460`, low-decile near `213-265`, or floor damage versus `screen_0005`.
- `PiecewiseExposureSaturationSurface`
  - Layer mutation: layer 3 shared-to-side exposure translator.
  - Interface boundary: dead-zone plus convex-tail exposure adds side protection only.
  - Forbidden consumers: shared fee compression, opportunity cuts, refill, recapture, inventory, and layer-4 allocation ledgers.
  - Kill signature: no-op phenotype, `quote_selectivity_ratio > 24`, `time_weighted_mean_fee > 0.00520`, low-retail below `416.8`, or broad shared-spread behavior.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round33/monotone_evidence_firewall.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round33/adverse_benign_non_substitution.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round33/protection_debt_repayment_gate.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round33/convex_adverse_envelope.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round33/counterfactual_fill_regret_bound.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round33/piecewise_exposure_saturation_surface.sol`
- Bounded follow-up inside the winning topology: `artifacts/scratch_probes/apr21-screen490-1431/round33/monotone_evidence_firewall_strict.sol`

### Probe Results

- `MonotoneEvidenceFirewall`
  - Mean edge: `486.7591690495959`
  - Delta vs `screen_0005`: `-0.25319491283602247`
  - Key profile: `arb_loss_to_retail_gain=0.09420493630712183`, `quote_selectivity_ratio=19.651786668260158`, `time_weighted_mean_fee=0.004793708475335394`
  - Floor slices: `low_decile_mean_edge=371.2895280521933`, `low_retail_mean_edge=416.7251449452739`, `low_volatility_mean_edge=464.1220110392283`
  - Outcome: constructive but sub-best. It improved versus the incumbent and preserved the intended band, but did not clear `screen_0005`.
- `AdverseBenignNonSubstitutionContract`
  - Mean edge: `485.924905294165`
  - Delta vs `screen_0005`: `-1.0874586682669474`
  - Key profile: `arb_loss_to_retail_gain=0.09910214188201702`, `quote_selectivity_ratio=21.159862668820136`, `time_weighted_mean_fee=0.004683496458984481`
  - Floor slices: `low_decile_mean_edge=370.6364306899167`, `low_retail_mean_edge=415.81927750720826`, `low_volatility_mean_edge=463.37628009558426`
  - Outcome: killed as near-incumbent / sub-best token separation. It avoided collapse but gave back floors and did not become a new owner.
- `ProtectionDebtRepaymentGate`
  - Mean edge: `407.379989838783`
  - Delta vs `screen_0005`: `-79.63237412364896`
  - Key profile: `arb_loss_to_retail_gain=0.25490686152748937`, `quote_selectivity_ratio=70.58786749984458`, `time_weighted_mean_fee=0.003611199354167352`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=361.3718231309885`, `low_volatility_mean_edge=415.0813721250534`
  - Outcome: hard kill as over-open release despite the debt vocabulary. The state update acted like a hidden repair/release path rather than repayment discipline.
- `ConvexAdverseEnvelope`
  - Mean edge: `485.9013953244173`
  - Delta vs `screen_0005`: `-1.11096863801464`
  - Key profile: `arb_loss_to_retail_gain=0.0994471997407848`, `quote_selectivity_ratio=21.30193336719838`, `time_weighted_mean_fee=0.004668458868335295`
  - Floor slices: `low_decile_mean_edge=370.7897871399368`, `low_retail_mean_edge=415.86354550928695`, `low_volatility_mean_edge=463.3043710028312`
  - Outcome: killed as no-op / sub-incumbent convex envelope. The bounded tail was too weak to make a new phenotype.
- `CounterfactualFillRegretBound`
  - Mean edge: `421.6665727578072`
  - Delta vs `screen_0005`: `-65.34579120462473`
  - Key profile: `arb_loss_to_retail_gain=0.22312938691868034`, `quote_selectivity_ratio=56.06677786424217`, `time_weighted_mean_fee=0.003979707688195616`
  - Floor slices: `low_decile_mean_edge=226.12395268507464`, `low_retail_mean_edge=375.8892975999733`, `low_volatility_mean_edge=415.84628184171777`
  - Outcome: hard kill as prior-markout / over-open release replay. Outside vocabulary did not help because outcome memory still routed into a floor-damaging phenotype.
- `PiecewiseExposureSaturationSurface`
  - Mean edge: `485.95461617525126`
  - Delta vs `screen_0005`: `-1.0577477871806877`
  - Key profile: `arb_loss_to_retail_gain=0.09956296934263707`, `quote_selectivity_ratio=21.35426544558037`, `time_weighted_mean_fee=0.004662439436110097`
  - Floor slices: `low_decile_mean_edge=370.69582954982866`, `low_retail_mean_edge=415.97141646077813`, `low_volatility_mean_edge=463.32136635539996`
  - Outcome: killed as near-incumbent / no-op side translator. It did not create enough tail activation to move outcome space.
- `MonotoneEvidenceFirewallStrict`
  - Mean edge: `487.1624615941965`
  - Delta vs `screen_0005`: `+0.15009763176453816`
  - Key profile: `arb_loss_to_retail_gain=0.09172397699712187`, `quote_selectivity_ratio=18.883566189778758`, `time_weighted_mean_fee=0.004857344003526725`
  - Floor slices: `low_decile_mean_edge=371.58639269782276`, `low_retail_mean_edge=417.1901099045671`, `low_volatility_mean_edge=464.6778227891047`
  - Outcome: selected for canonical retained eval because it beat `screen_0005` and improved leakage/selectivity plus low-retail / low-volatility floors while keeping fee band close to prior best raw.

### Retained Eval

- Canonical eval: `screen_0006` / `monotone-evidence-firewall-strict`
- Status: `discard` because it did not clear the promotion margin, but it is the new best raw retained branch.
- Delta vs incumbent: `+1.2386908905246514`
- Promotion margin: `20.617586659996192`
- Retained state after Round 33:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0006`
  - best raw mean edge: `487.1624615941965`
  - best raw gap to breakout target: `2.8375384058035`

### Validation And Commands

- Validated all six accepted scratch sources with `uv run amm-match validate`.
- Ran scratch probes with `uv run amm-match hill-climb probe --stage screen --json` and wrote each result to the matching concrete JSON file listed in the probe sources/results above.
- Ran the retained eval:
  - `uv run amm-match hill-climb eval --run-id apr21-screen490-1431 --stage screen --label monotone-evidence-firewall-strict --description "Round 33 retained spend: strict monotone evidence firewall that can only raise protection-side evidence, selected after scratch beat screen_0005 while improving leakage/selectivity and tracked floor slices." --json artifacts/scratch_probes/apr21-screen490-1431/round33/monotone_evidence_firewall_strict.sol > artifacts/scratch_probes/apr21-screen490-1431/round33/retained_eval_monotone_evidence_firewall_strict.json`
- Verified retained status with `uv run amm-match hill-climb status --run-id apr21-screen490-1431 --json`.

### Updated Entropy Discipline

- One-way evidence firewalls are live, but the positive result is the interface invariant, not a license to spend Round 34 on firewall coefficients. The next batch should use `screen_0006` as the measurement anchor while adding a different primary owner.
- Debt-before-repair and counterfactual regret memories are killed in their current form. Both replayed the old over-open release basin despite distinct vocabulary.
- Adverse/benign token separation, convex envelopes, and piecewise side translators were too weak in this implementation; do not retry them as support-only no-op guards unless a new primary topology supplies the movement.
- Keep the next proposer/critic batch away from local `screen_0006` polish. Prefer a new module/interface that can stack with the one-way firewall without broadening release, opportunity, recapture, refill, inventory, or final quote behavior.
