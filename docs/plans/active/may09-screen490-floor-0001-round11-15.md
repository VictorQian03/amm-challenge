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
