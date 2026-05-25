# may09-screen490-floor-0001 Rounds 11-15

This chunk continues the active floor-seed lane after `screen_0004` / `OracleTradeToxCoef6500` became the live best raw.

## Round 11: Hyperparameter Sweep

### Constraints

- Current user boundary: no oracle implementation access; use live retained state and scratch probes only.
- Active retained incumbent: `screen_0001` / `LatentStateQuoteEngine` at `487.01236396243195`.
- Starting best raw: `screen_0004` / `OracleTradeToxCoef6500` at `489.8573894977019`.
- Breakout target: `490`.
- Retained eval rule: only write the canonical lane after scratch candidates beat live best raw or materially improve floor-risk ownership.

### Sweep Surface

- Generated variants: `100` scratch smoke probes across state memory, state decay, stress observation, flow, risk protection, cut caps, current trade-tox coefficients, near-frontier bases, and second-order combinations.
- Scratch sources and bulk summary output were removed after the durable comparisons below were captured; they are not retained artifacts.

### Stage Results

Current best raw baseline:

| Stage | Mean | Low decile | Low retail | Low volatility | Leak | QSR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `screen` | `489.8573894977019` | `372.30960999069316` | `418.8324844879155` | `467.09686882292414` | `0.08118104808611501` | `15.850160234617611` |
| `climb` | `484.4376558588365` | `335.4801280097374` | `393.43015218449017` | `485.77211871880013` | `0.08856878706310485` | `17.276198749053343` |
| `confirm` | `470.8480041814009` | `328.1154987921714` | `390.3282518597198` | `476.56216607340934` | `0.08812734728560366` | `17.057088263096194` |

Best retained candidate, `FlowDirectionalRisk280`:

| Stage | Mean | Delta vs current best raw | Low decile delta | Low retail delta | Low volatility delta | Leak delta | QSR delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `screen` | `490.75833078204124` | `+0.9009412843393534` | `+0.9525976210613862` | `+0.8281336396844689` | `+1.0313072095368006` | `+0.00027060863253217105` | `+0.2312634966786753` |
| `climb` | `485.27475773569165` | `+0.8371018768551721` | `+0.7656743708470231` | `+0.8066877949523373` | `+0.8903516278108822` | `+0.00018839264439564352` | `+0.22337306717784244` |
| `confirm` | `471.6931759281264` | `+0.845171746725498` | `+0.7131416595552764` | `+0.735786402740132` | `+0.8393626040870572` | `+0.00021534785308487125` | `+0.22282867728604927` |

Second-order alternatives:

| Candidate | Screen mean | Climb mean | Confirm mean | Decision |
| --- | ---: | ---: | ---: | --- |
| `HypFlowDir280AlphaPassive22Protection5100` | `491.17856231010995` | `485.76537570020946` | not run | rejected for promotion; stronger screen/climb mean but worse leakage/selectivity than `FlowDirectionalRisk280` |
| `HypFlowDir280Cluster7000Boost7000` | `490.63695176167863` | `485.99013997929734` | `471.107174026445` | rejected for promotion; confirm worsened low-decile, low-retail, leakage, and selectivity |
| `HypCluster7000Boost7000` | `489.9334911106756` | `485.25307377543436` | `470.27136440242765` | rejected; clean climb profile did not hold on confirm |

### Retained Eval

- Canonical retained eval opened: `screen_0005` / `flow-dir-risk-280` / `FlowDirectionalRisk280`.
- Retained screen mean: `490.75833078204124`.
- Status: `discard`, because the incumbent promotion margin remains `20.821171777666088`.
- New live best raw: `screen_0005`.
- Source snapshot: `artifacts/hill_climb/may09-screen490-floor-0001/snapshots/8734ce7ce521f9b8e61e3ed1bda07c15ee29bf71a6dc771bc7fe66bbf876468a.sol`.

### Decision

- Retain `FlowDirectionalRisk280` as the new best raw branch for continuation.
- Treat the change as a narrow flow-directional-risk coefficient improvement, not a new search frame.
- Do not continue coefficient-only flow-directional-risk polish unless the next proposal changes the consumer contract or directly targets the small leakage/selectivity cost.
- Do not promote the second-order combo branch despite higher screen/climb means; holdout confirm showed worse named floor and leakage/selectivity metrics.

## Round 12: Flow-Risk Consumer Boundary Sweep

### Constraints And Admission

- User ceiling: stop at `screen`; do not run `climb` or `confirm`.
- Primary base: retained `screen_0005` / `FlowDirectionalRisk280` at `490.75833078204124`.
- Frozen comparison base: retained `screen_0004` / `OracleTradeToxCoef6500` only as a control; no local trade-tox reopening.
- The prior broad Round 11 sweep already saturated standalone memory, decay, fee, refill, trade-tox, and flow-risk coefficient tuning. Round 12 therefore admitted four bounded consumer interactions that directly target `screen_0005`'s small leakage/selectivity cost.

### Sweep Surface

| Family | Levels | Contract Being Tested |
| --- | ---: | --- |
| `protected_flow_reserve` | `4` | Reserve `25%`, `50%`, `75%`, or `100%` of flow-derived protection from same-quote opportunity-cut spend-back. |
| `flow_optional_offset_gate` | `4` | Scale healing/refill offsets to `0%`, `25%`, `50%`, or `75%` only while aligned flow risk is active. |
| `extension_tail_risk` | `4` | Add a bounded protection surcharge only when extension evidence exceeds the existing tail threshold. |
| `tail_protected_reserve` | `4` | Combine a tail-only surcharge with bounded protected reserve. |

- Evaluated `18` smoke probes including both controls.
- Screened only the surviving tail-only branch at levels `20`, `40`, and `60`, plus the `screen_0005` control.
- Compact reproducible evidence is under `artifacts/scratch_probes/may09-screen490-floor-0001/round12_parameter_sweep/`; bulk generated sources and full probe payloads were removed after producing summaries.

### Smoke Triage

| Candidate | Mean | Leak | QSR | Low decile | Low volatility | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `base_flow_dir_280` | `500.87626155657506` | `0.07566421481038242` | `14.611517233274078` | `367.4219121310769` | `471.248059270886` | control |
| `extension_tail_surcharge_40` | `500.88587825362606` | `0.07566628147074585` | `14.610891990218496` | `367.41683887032667` | `471.25922172938596` | screen |
| `flow_offset_scale_7500` | `475.73231900235874` | `0.12686542599344983` | `26.549736750948796` | `222.85894799910943` | `404.33636765041206` | reject |
| `flow_reserve_2500` | `442.6080200999101` | `0.18787934262443162` | `40.91617975245058` | `222.85894799910943` | `316.81028967278513` | reject |

### Screen Results

| Candidate | Mean | Delta vs `screen_0005` | Leak delta | QSR delta | Low decile delta | Low retail delta | Low volatility delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `base_flow_dir_280` | `490.75833078204124` | `0` | `0` | `0` | `0` | `0` | `0` |
| `extension_tail_surcharge_20` | `490.73980570811455` | `-0.018525073926696223` | `-0.00001244401656999572` | `-0.00479293930768776` | `-0.03282219063640923` | `+0.0021678298626852666` | `-0.017601308372434232` |
| `extension_tail_surcharge_40` | `490.7375193830867` | `-0.02081139895454953` | `-0.000013320301733343864` | `-0.005423711074815429` | `-0.03453781307848658` | `+0.0039374190540115706` | `-0.025130557884722293` |
| `extension_tail_surcharge_60` | `490.7257966551642` | `-0.03253412687706714` | `-0.0000133869123890018` | `-0.007820620696794123` | `-0.023577676270690517` | `-0.0021077260342394766` | `-0.03416989802076387` |

### Decision

- No retained eval was justified; canonical best raw remains `screen_0005` / `FlowDirectionalRisk280`.
- Flow-protection reserve and active-flow healing/refill gating do not repair the measured cost. They reproduce the cut-boundary starvation / floor-collapse basin immediately at smoke.
- Tail-only extension protection is the only non-collapsing family in this batch, but its small leakage/selectivity repair costs mean and named floor slices at screen. Do not continue surcharge coefficient polish.
- Further continuation needs a different consumer contract that preserves the `screen_0005` floor gains without restricting benign cut paths or merely raising protection in extreme flow tails.

## Round 13: Direct Screen Threshold Search

### Scope

- User stop rule: continue testing strategy variants until one scores at least `+1.0` above live best raw on `screen`; only result bookkeeping remained mandatory for this round.
- Baseline: retained `screen_0005` / `FlowDirectionalRisk280` at `490.75833078204124`.
- Required screen threshold: `491.75833078204124`.
- Protected oracle implementation was not inspected.

### Search And Result

- A scratch search generated `108` broad candidates over live thresholds, risk/protection weights, fee terms, passive-recapture controls, and selected interactions; `25` smoke leaders were screened.
- The first narrowing identified compatible positives in lower event carry and stronger passive recapture. A second `16`-candidate stacked smoke batch produced `14` non-collapsing candidates for screen.

| Candidate | Screen mean | Delta vs `screen_0005` | Low decile | Low retail | Low volatility | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `Event140Recapture` | `491.910339497031` | `+1.1520087149897336` | `374.1601620732385` | `420.7386906088814` | `469.34376177670674` | retained best raw / stop |
| `stack_event160_recapture` | `491.810622669846` | `+1.0522918878047562` | `374.1681023850458` | `420.6948383113722` | `468.95620897945696` | threshold-clearing scratch alternative |
| `stack_event160_flow220_recap_strong` | `491.7469501964255` | `+0.9886194143842317` | `374.20225799167497` | `420.62689833785424` | `469.0036888988806` | below stop threshold |

### Retained Eval And Decision

- Canonical retained eval: `screen_0006` / `event140-recapture` / `Event140Recapture`.
- Source change from `screen_0005`: event carry `220 -> 140`, passive-recapture alpha `18 -> 22`, passive recapture cut `1550 -> 1750`, inventory-centering offset `700 -> 850`, and centering cap `1400 -> 1600`.
- Retained status is still `discard` relative to the seeded incumbent because the harness promotion margin is larger than this delta; under the explicit Round 13 goal, the required best-raw improvement is achieved.
- Evidence and reproducer: `artifacts/scratch_probes/may09-screen490-floor-0001/round13_direct_screen_search/`.
- Stop at `screen` as instructed; no `climb` or `confirm` claim is made for this candidate.
