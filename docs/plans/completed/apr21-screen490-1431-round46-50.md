# apr21-screen490-1431 rounds 46-50

Run index: [apr21-screen490-1431.md](apr21-screen490-1431.md)

## Opening Constraints

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard entering this chunk: `screen_0008` / `weak-consistency-event-feasibility-mask` at `488.03274719863765`.
- Best raw gap to breakout target: `1.9672528013623468`.
- Breakout target: `490`.
- Round 45 closed with no canonical retained eval.
- Do not spend the next round on weak-consistency residual coefficient tuning, queue/depth/passive-fill/latency, temporal clocks, Kyle/impact coefficients, LVR floor tuning, direct fee rights, final quote, layer 5/6, refill, recapture, opportunity, relief deletion, support-only controls, account/allocation/cost-share vocabulary, or generic market-design relabeling.
- The next accepted batch needs at least four critic-approved strategy design improvements before source work starts.
- The proposer/critic loop must treat `SupplyFunctionServiceCurve` as a diagnostic outcome-space move, not a target for coefficient polish, unless the proposal has a hard no-floor-loss boundary tied to `screen_0008`.

## Round 46: No-Floor-Loss Service-Capacity Relaxation

### Starting State

- Active retained lane: `apr21-screen490-1431`.
- Official incumbent: `screen_0001` / `starter-baseline-post-fix` at `485.92377070367183`.
- Best raw retained discard entering the round: `screen_0008` / `weak-consistency-event-feasibility-mask` at `488.03274719863765`.
- Breakout target: `490`.
- Round 45 closed with no retained eval candidate. `SupplyFunctionServiceCurve` improved leakage/selectivity but lost mean and all tracked floors, so Round 46 allowed only a narrow service-capacity relaxation with hard no-floor-loss boundaries.

### Subagent Workflow

- Topology proposer supplied six service-capacity candidates:
  - `FloorParityServiceCurve`
  - `IsofloorServiceSlopeSplitter`
  - `RetailFloorFirstServiceOwner`
  - `VolatilityIsoquantServiceMap`
  - `ProtectedSideServiceElasticity`
  - `DecileParityServiceThrottle`
- Saturation critic accepted four worker contracts under tightened boundaries:
  - Accepted `IsofloorServiceSlopeSplitter` only as a layer-2 split between floor-preserving and floor-risking service slope regimes.
  - Accepted `RetailFloorFirstServiceOwner` only as a retail floor owner, not a local retry of `RetailFloorFirstStatePartition`.
  - Accepted `VolatilityIsoquantServiceMap` only as protected-side risk evidence, not a volatility-indexed fee or base-spread term.
  - Accepted `ProtectedSideServiceElasticity` only as one-way protected-side elasticity evidence that cannot lower protection or authorize benign-side service admission.
  - Rejected `FloorParityServiceCurve` as direct `SupplyFunctionServiceCurve` naming churn.
  - Deferred / rejected `DecileParityServiceThrottle` as too close to service-admission and throttle vocabulary.
- Enforced entropy constraints:
  - four accepted scratch paths before any retained decision
  - no retained-ledger edits by workers
  - no `Reference.sol` inspection
  - no queue/depth/passive-fill/latency, temporal clocks, Kyle/impact coefficients, LVR floor tuning, direct fee rights, final quote, layer 5/6, refill, recapture, opportunity, relief deletion, account/allocation/cost-share vocabulary, or generic market-design relabeling
  - no bounded coefficient tweak after service-curve overcharge/floor-loss, downstream floor-admission collapse, geometry-codec plateau, or hidden-release signatures

### Accepted Scratch Contracts

- `IsofloorServiceSlopeSplitter`
  - Layer mutation: layer-2 splitter between floor-preserving and floor-risking service slope regimes.
  - Interface boundary: protected-side evidence may emit only when a local floor proxy indicates floor parity.
  - Forbidden consumers: direct fee changes, shared-spread adders, final quote, relief/release, capacity windows, queue/depth, volatility fee rent, coefficient-only slope retuning.
  - Kill signature: mean below `screen_0008`, any floor below `screen_0008`, leakage above `0.08680487844146438` unless all floors improve, selectivity above `19.5`, fee outside `0.00490-0.00518`, or service-curve overcharge / floor-loss.
- `RetailFloorFirstServiceOwner`
  - Layer mutation: layer-2/3 retail-floor preservation gate before protection sizing.
  - Interface boundary: service-capacity evidence is suppressed under hazard, flow pressure, one-sided flow, divergence, short gaps, or high imbalance.
  - Forbidden consumers: floor-partition coefficient polish, robust-demand bins, classifier-local abstention, account/allocation vocabulary, fee compression, relief/release, final quote, layer 5/6.
  - Kill signature: low-retail below `417.8656683116062`, low-decile below `372.41891117598567`, mean below `screen_0008`, fee above `0.00518`, selectivity outside `15.5-19.5`, or classifier-local floor-drag / overcharge.
- `VolatilityIsoquantServiceMap`
  - Layer mutation: layer-1/2 volatility isoquant evidence map.
  - Interface boundary: evidence is reduced by calm/passive service relief and is only applied to existing protected-side risk.
  - Forbidden consumers: volatility base fee, LVR floor tuning, geometry-codec no-op, direct spread adders, liquidity-shortfall placement, capacity-window admission, final quote.
  - Kill signature: low-volatility below `465.1871007698987`, any other floor below anchor, mean below anchor, fee above `0.00518`, selectivity above `19.5`, or post-spread fee-rent / geometry-codec plateau.
- `ProtectedSideServiceElasticity`
  - Layer mutation: layer-2 protected-side elasticity evidence.
  - Interface boundary: may raise protection evidence on the protected side, but cannot lower protection or authorize benign-side service admission.
  - Forbidden consumers: safe-side admission, capacity service windows, relief/release, direct fee rights, opportunity/refill/recapture, final quote, layer 5/6, queue/depth/passive-fill.
  - Kill signature: any floor below `screen_0008`, leakage above anchor unless all floors improve, selectivity above `19.5`, fee below `0.00490` or above `0.00518`, downstream floor-admission collapse, or hidden-release.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round46/isofloor_service_slope_splitter.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round46/retail_floor_first_service_owner.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round46/volatility_isoquant_service_map.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round46/protected_side_service_elasticity.sol`

### Probe Results

- `IsofloorServiceSlopeSplitter`
  - Mean edge: `485.9113006889398`
  - Delta vs `screen_0008`: `-2.1214465096978756`
  - Key profile: `arb_loss_to_retail_gain=0.09963951351708092`, `quote_selectivity_ratio=21.35839240564946`, `time_weighted_mean_fee=0.004665122338080346`
  - Floor slices: `low_decile_mean_edge=370.7782289826529`, `low_retail_mean_edge=415.9305904236997`, `low_volatility_mean_edge=463.26233901577945`
  - Outcome: killed as near-incumbent service-slope no-op with floor loss versus `screen_0008`.
- `RetailFloorFirstServiceOwner`
  - Mean edge: `485.6223109962206`
  - Delta vs `screen_0008`: `-2.4104362024170314`
  - Key profile: `arb_loss_to_retail_gain=0.10036280969700188`, `quote_selectivity_ratio=21.60261423893202`, `time_weighted_mean_fee=0.0046458640878810405`
  - Floor slices: `low_decile_mean_edge=370.5119988114744`, `low_retail_mean_edge=415.5873369552821`, `low_volatility_mean_edge=463.0463915684218`
  - Outcome: killed as retail-floor service owner floor drag. It missed every hard no-floor-loss threshold and degraded leakage/selectivity.
- `VolatilityIsoquantServiceMap`
  - Mean edge: `485.92377070367183`
  - Delta vs `screen_0008`: `-2.108976494965816`
  - Key profile: `arb_loss_to_retail_gain=0.09961822784430861`, `quote_selectivity_ratio=21.366983876018754`, `time_weighted_mean_fee=0.004662250340166877`
  - Floor slices: `low_decile_mean_edge=370.69865470550553`, `low_retail_mean_edge=415.9137203431734`, `low_volatility_mean_edge=463.32099611706855`
  - Outcome: killed as incumbent-equivalent isoquant no-op. The evidence map produced no useful movement.
- `ProtectedSideServiceElasticity`
  - Mean edge: `485.90438006171195`
  - Delta vs `screen_0008`: `-2.1283671369257036`
  - Key profile: `arb_loss_to_retail_gain=0.09951158542946661`, `quote_selectivity_ratio=21.323072997768747`, `time_weighted_mean_fee=0.004666850103635604`
  - Floor slices: `low_decile_mean_edge=370.84049363351295`, `low_retail_mean_edge=415.9363874607148`, `low_volatility_mean_edge=463.27682046366533`
  - Outcome: killed as near-incumbent protected-side elasticity no-op with floor loss versus `screen_0008`.

### Decision

- No Round 46 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0008`
  - best raw mean edge: `488.03274719863765`
  - best raw gap to breakout target: `1.9672528013623468`

### Validation And Commands

- Validated all four accepted scratch sources with `uv run amm-match validate`.
- Ran scratch probes with `uv run amm-match hill-climb probe --stage screen --json` and wrote each result to the matching concrete JSON file listed in the probe sources/results above.

### Updated Entropy Discipline

- The narrow service-capacity relaxation did not recover the Round 45 floor-loss problem. Three accepted contracts were near-incumbent variants with tracked floor loss versus `screen_0008`, and the volatility isoquant map was exactly incumbent-equivalent.
- Do not spend Round 47 on more service-capacity curves, slope splitters, retail-floor gates, isoquant maps, or protected-side elasticity unless the seed/anchor frame changes first.
- The next productive move likely needs a different seed / anchor frame away from `screen_0008`-adjacent service-capacity repair, or a new non-service primary owner that is mechanically distinct from labels, accounts, allocation, fee rights, downstream relief, and service gating.

## Round 47: Scratch-Only Retained-Snapshot Seed Frame

### Starting State

- Active retained lane: `apr21-screen490-1431`.
- Official incumbent: `screen_0001` / `starter-baseline-post-fix` at `485.92377070367183`.
- Best raw retained discard entering the round: `screen_0008` / `weak-consistency-event-feasibility-mask` at `488.03274719863765`.
- Breakout target: `490`.
- Round 46 closed with no retained eval candidate. Current `contracts/src/StarterStrategy.sol` is still the official incumbent snapshot, so Round 47 used a scratch-only seed/anchor-frame change from retained raw snapshots while keeping retained ledgers and `StarterStrategy.sol` untouched.

### Subagent Workflow

- Topology proposer supplied six snapshot-seeded candidates:
  - `SplitBusFeasibilityUnion` from `screen_0003`
  - `SelectorFeasibilityCrosscheck` from `screen_0005`
  - `QuantileFirewallIngress` from `screen_0007`
  - `FirewallEventPathConjunction` from `screen_0006`
  - `FeasibilitySplitBusBackport` from `screen_0008`
  - `EarlyBurstFloorChecksum` from `screen_0002`
- Saturation critic accepted exactly four worker contracts:
  - Accepted `SplitBusFeasibilityUnion` as the cleaner split-bus / feasibility union from the older split-bus seed.
  - Accepted `SelectorFeasibilityCrosscheck` only inside floor-preserving selector regimes.
  - Accepted `QuantileFirewallIngress` only as bounded tail-state ingress into one-way firewall evidence.
  - Accepted `FirewallEventPathConjunction` as an event-path validity precondition before monotone firewall emission.
  - Rejected `FeasibilitySplitBusBackport` as too close to local `screen_0008` residual replay.
  - Deferred `EarlyBurstFloorChecksum` because burst carry remained a narrow adjunct with known low-decile collision risk.
- Enforced entropy constraints:
  - four accepted scratch paths before any retained decision
  - no retained-ledger edits by workers
  - no `StarterStrategy.sol` edits
  - no `Reference.sol` inspection
  - no generic service-capacity repair, weak-consistency residual coefficient tuning, queue/depth/passive-fill/latency, temporal clocks, direct fee rights, final quote, layer 5/6, refill, recapture, opportunity, relief deletion, account/allocation/cost-share vocabulary, or generic market-design relabeling

### Accepted Scratch Contracts

- `SplitBusFeasibilityUnion`
  - Seed: `screen_0003` snapshot `artifacts/hill_climb/apr21-screen490-1431/snapshots/de77c9a2a79535a7081148786f90a551cf04fc5387c2954f7ab977f71c88891e.sol`
  - Layer mutation: upstream evidence union between information/liquidity separation and event-path feasibility.
  - Interface boundary: keep information/liquidity separation disjoint from event-path feasibility; neither side may lower protection, compress fees, or feed downstream relief.
  - Kill signature: mean below `screen_0008`, any floor below anchor, leakage above `0.08680487844146438` unless all floors improve, selectivity above `19.5`, or hidden-release / open-leak profile.
- `SelectorFeasibilityCrosscheck`
  - Seed: `screen_0005` snapshot `artifacts/hill_climb/apr21-screen490-1431/snapshots/3f4bb9e4883515bf62bce866f36815402f6299c9e03b099e1f15f159acec4d9a.sol`
  - Layer mutation: feasibility evidence inside floor-preserving selector regimes.
  - Interface boundary: no selector threshold retuning, no fee-band polish, no broad release when selector confidence rises.
  - Kill signature: any tracked floor below `screen_0008`, mean below anchor, selectivity above `19.5`, fee outside `0.00490-0.00518`, or classifier-local floor-drag / selector-polish no-op.
- `QuantileFirewallIngress`
  - Seed: `screen_0007` snapshot `artifacts/hill_climb/apr21-screen490-1431/snapshots/7fce3149b3de21ffd8894fb9593eb111219b2b99bdbc67cbe8eef1847436f28c.sol`
  - Layer mutation: bounded tail-state ingress into one-way firewall evidence.
  - Interface boundary: tail buckets can raise protection evidence, but cannot become consumers, widen release, lower fees, or open benign-side admission.
  - Kill signature: tail-consumer over-open profile, selectivity above `19.5`, leakage above anchor, any floor below anchor, or phenotype-identical tail/firewall threshold polish.
- `FirewallEventPathConjunction`
  - Seed: `screen_0006` snapshot `artifacts/hill_climb/apr21-screen490-1431/snapshots/f3c1f5f28f6d418320e0cee9d3eca83523852861dbadedba2bcc85e1d41d5e0c.sol`
  - Layer mutation: event-path validity precondition before monotone firewall emission.
  - Interface boundary: cannot authorize release, weaken firewall output, alter final quote, or become residual coefficient tuning.
  - Kill signature: mean below anchor, any floor below anchor, selectivity above `19.5`, leakage above anchor without floor gains, or firewall/event-feasibility no-op plateau.

### Probe Sources

- `artifacts/scratch_probes/apr21-screen490-1431/round47/split_bus_feasibility_union.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round47/selector_feasibility_crosscheck.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round47/quantile_firewall_ingress.sol`
- `artifacts/scratch_probes/apr21-screen490-1431/round47/firewall_event_path_conjunction.sol`

### Probe Results

- `SplitBusFeasibilityUnion`
  - Mean edge: `445.3607057703515`
  - Delta vs `screen_0008`: `-42.67204142828615`
  - Key profile: `arb_loss_to_retail_gain=0.05773257311845217`, `quote_selectivity_ratio=5.975423646049786`, `time_weighted_mean_fee=0.009661670291213214`
  - Floor slices: `low_decile_mean_edge=338.1721773521499`, `low_retail_mean_edge=383.5558271709335`, `low_volatility_mean_edge=425.92481829271105`
  - Outcome: killed as split-bus / feasibility overcharge floor loss. It improved leakage/selectivity only by charging far above the accepted fee band and breaking all tracked floors.
- `SelectorFeasibilityCrosscheck`
  - Mean edge: `439.1583825614714`
  - Delta vs `screen_0008`: `-48.87436463716625`
  - Key profile: `arb_loss_to_retail_gain=0.18514164362407445`, `quote_selectivity_ratio=42.51071826091918`, `time_weighted_mean_fee=0.004355175616834456`
  - Floor slices: `low_decile_mean_edge=246.91899246055303`, `low_retail_mean_edge=399.19595272591783`, `low_volatility_mean_edge=416.0914116831347`
  - Outcome: killed as selector crosscheck hidden release / floor collapse. The selector seed did not prevent downstream leakage once feasibility evidence entered the path.
- `QuantileFirewallIngress`
  - Mean edge: `408.49695556617877`
  - Delta vs `screen_0008`: `-79.53579163245888`
  - Key profile: `arb_loss_to_retail_gain=0.25041808935996307`, `quote_selectivity_ratio=67.43692877299972`, `time_weighted_mean_fee=0.003713367348072723`
  - Floor slices: `low_decile_mean_edge=213.53482106574324`, `low_retail_mean_edge=362.6554657644194`, `low_volatility_mean_edge=416.39488605722175`
  - Outcome: hard kill as tail-firewall ingress hidden release. Tail buckets reached the same over-open basin that prior tail-consumer and run-length segment labels hit.
- `FirewallEventPathConjunction`
  - Mean edge: `483.8246115813607`
  - Delta vs `screen_0008`: `-4.208135617276923`
  - Key profile: `arb_loss_to_retail_gain=0.08108003052369148`, `quote_selectivity_ratio=14.381566433176816`, `time_weighted_mean_fee=0.00563777464022612`
  - Floor slices: `low_decile_mean_edge=369.70642539817646`, `low_retail_mean_edge=414.9399888853488`, `low_volatility_mean_edge=460.6518219236478`
  - Outcome: killed as firewall/event-path overcharge floor loss. It improved leakage/selectivity but broke mean, fee band, and all tracked floors.

### Decision

- No Round 47 scratch candidate earned a canonical retained eval.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0008`
  - best raw mean edge: `488.03274719863765`
  - best raw gap to breakout target: `1.9672528013623468`

### Validation And Commands

- Validated all four accepted scratch sources with `uv run amm-match validate`.
- Ran scratch probes with `uv run amm-match hill-climb probe --stage screen --json` and wrote each result to the matching concrete JSON file listed in the probe sources/results above.

### Updated Entropy Discipline

- Scratch-only retained-snapshot seeding did not unlock the target. The older split-bus and firewall seeds could improve leakage/selectivity, but only through overcharge and floor loss; the selector and tail seeds collapsed into hidden release / floor collapse.
- Do not spend Round 48 on snapshot backports that merely union split-bus, feasibility, selector, tail, or firewall evidence. These were materially different seeds and still replayed known basins.
- Continuing likely requires a genuinely new non-service, non-label primary owner, or a higher-level harness/search decision about whether this retained lane is saturated below the `490` breakout target.

## Round 48: Saturation Gate

### Starting State

- Active retained lane: `apr21-screen490-1431`.
- Official incumbent: `screen_0001` / `starter-baseline-post-fix` at `485.92377070367183`.
- Best raw retained discard entering the round: `screen_0008` / `weak-consistency-event-feasibility-mask` at `488.03274719863765`.
- Breakout target: `490`.
- Rounds 45-47 exhausted service-capacity repair, no-floor-loss service relaxation, and scratch-only retained-snapshot seed unions / backports without producing a retained candidate.

### Subagent Workflow

- Topology proposer was asked to produce at least four genuinely distinct, non-service, non-label primary-owner designs under the current ban set, or state a hard blocker.
- The proposer named six possible shapes but rejected them as accepted-worthy:
  - `InvariantExcursionHold`: marginal only; too close to curvature / geometry adjuncts and not a credible primary breakout owner.
  - `FloorConsensusSpreadHold`: rejected as worst-slice / overcharge replay.
  - `BenignCaptureBandCap`: rejected as conservation / cap / certificate floor-drag replay.
  - `BoundedBandpassAdjunct`: rejected as primary; geometry-codec support-only without a new downstream owner.
  - `StaticSpreadMonotonicityProof`: rejected as Round 43 mechanical isolation / monotonicity replay.
  - `ReserveNeutralityChecksum`: rejected as too close to Round 45 reserve-score failure and broad-protection starvation.
- No critic or worker subagents were launched because the four-design floor could not be met.

### Blocker

- The current banned-family set removes service-capacity repair, retained-snapshot seed recombination, weak-consistency residual tuning, queue/depth/passive-fill/latency, temporal clocks, direct fee rights, final quote, refill/recapture/opportunity replay, relief deletion, account/allocation/cost-share vocabulary, causal/adverse-mass labels, generic uncertainty labels, robust-demand bins, liquidity-shortfall placement, source deconvolution, and run-length/context segment labels.
- Operator update after the Round 48 blocker: loosen the layer 5/6 restriction for future planning. Layer 5/6 can receive at most one tightly bounded diagnostic slot when the proposer imports genuinely out-of-distribution vocabulary or web-search mechanisms and the contract forbids incumbent-local exploit polish; do not count more in-distribution AMM, market-design, LOB, hazard, refill, recapture, inventory, opportunity, or final-quote searches as entropy.
- The proposer could not defend four designs with positive expected movement and clean novelty after those exclusions.
- Starting Round 48 source work under the current constraints would be naming churn.

### Decision

- No Round 48 scratch source work was started.
- No retained eval was spent.
- Retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0008`
  - best raw mean edge: `488.03274719863765`
  - best raw gap to breakout target: `1.9672528013623468`

### Required Operator Decision

- Retire this retained lane as saturated below the `490` breakout target and start a fresh run from a new seed / anchor frame.
- Or explicitly relax one banned family for a tightly bounded diagnostic batch with concrete kill thresholds.
- Under the current ban set, source work for Round 48 should not start.
