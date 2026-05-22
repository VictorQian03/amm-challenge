# Reference Oracle Evidence Cards

This is the reusable format for authorized `Reference.sol` studies. It keeps oracle-derived evidence useful for search while preserving the boundary that future agents should reuse phenotype, metric, and interface lessons, not implementation details.

Format choices follow OpenAI guidance: keep prompts simple and delimited, use structured fields that can be compared mechanically, and treat the prompt/evidence gate as an eval that is iterated against real failures. See OpenAI [reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), and [evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices).

## Evidence Card Template

Use this card when a future run is allowed to inspect or score an oracle comparator.

| Field | Required content |
| --- | --- |
| `boundary` | Oracle access status, allowed reuse level, and forbidden reuse. |
| `question` | Attribution, transplant, consumer-compatibility, or topology-knockout question. |
| `controls` | Stage, seed range, pairing method, metrics, and raw summary artifact paths. |
| `bases` | Live seed, active incumbent, parked anchors, and any oracle comparator. |
| `findings` | Compact evidence rows with delta, confidence, and interpretation. |
| `consumer_contract_lesson` | Primary owner, allowed consumers, forbidden consumers, failure basin, and kill signature. |
| `reuse_guidance` | Admit conditions, reject conditions, support-only uses, and next test before source work. |
| `anchor_map_entry` | Durable tag, compatibility rule, collision rule, and kill signature for `docs/combination_anchor_map.md`. |

## Card: May09 Reference Transplant Evidence

| Field | Value |
| --- | --- |
| `boundary` | User explicitly authorized a local `Reference.sol` comparator for the May13 study. Future reuse is phenotype, metric, and interface guidance unless the current task explicitly authorizes oracle access again. The oracle implementation is intentionally not committed. |
| `question` | Which Reference-derived design units are attribution-critical, plug-compatible, or useful only as high-level owner/consumer evidence for `may09-screen490-floor-0001`? |
| `controls` | Fixed-seed paired comparisons: `screen` seeds `0..31`, `climb` seeds `0..127`, and selected `confirm` seeds `1000..1511`. Metrics: `mean_edge`, `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, and floor slices. |
| `bases` | Active retained seed `screen_0001` / `seed-from-apr21-screen0005` / `LatentStateQuoteEngine` at `487.01236396243195`; source frame `RegimeSelectorStrongerFloor`; parked `WeakConsistencyEventFeasibilityMask` at `488.03274719863765`; parked `MajorizationRiskVectorFilter` at `487.7232131981818`; full Reference comparator. |
| `raw_summaries` | Local-only, not committed: `artifacts/scratch_probes/may09-screen490-floor-0001/oracle_ablation/analysis_summary.json`, `second_wave_summary.json`, and `transplant_summary.json`. |

### Findings

| Evidence unit | Result | Confidence | Reusable read |
| --- | ---: | --- | --- |
| Full Reference vs active seed | `+48..+53` edge across screen/climb/confirm | Strong, paired and holdout-positive | Oracle advantage is integrated estimator -> toxicity/protection -> side-protection -> fee ownership, not a single low-fee knob. |
| Standalone Reference fair-mid into frontier consumers | About `-72..-75` on screen and `-86..-89` on climb | Strong negative | Raw estimator publication is incompatible with current hazard/protection/opportunity consumers. |
| Shadow oracle evidence into one existing consumer | About `-78..-79` on screen | Strong negative | Private namespaces do not fix the consumer contract; existing shared spread, side protection, and opportunity veto still misconsume oracle-shaped evidence. |
| Reference stale-side protect/attract knockout | About `-117.5` on climb | Strong attribution | Stale-side protection must be a primary owner, not an additive side-risk term. |
| Reference lambda fee knockout | About `-40.2` on climb | Strong attribution | Arrival-rate / congestion fee ownership is primary; flow-size/activity fee terms are support. |
| Same-step fair-mid slowdown knockout | About `-10.4` on climb | Strong attribution | Same-step publication throttling is a real estimator-control surface. |
| `WeakConsistencyEventFeasibilityMask + ref_trade_tox_boost` | `+1.3047780456046092` confirm delta over 512 seeds | Only robust direct transplant | Treat as a useful phenotype/interface signal; direct transplant work still needs explicit authorization. |
| Tail compression, direction-only state, cubic toxicity, sigma-tox cross | Neutral or tiny negative | Strong enough to deprioritize | Do not anchor future rounds on these support controls. |
| Current frontier event carry and quiet recenter | Large negative topology knockouts | Strong topology evidence | These layers are load-bearing; do not delete them as simplification. |
| Shared calm rebate and refill auction | Near-neutral topology knockouts | Diagnostic only | Useful only as small diagnostics around a larger owner change. |

### Consumer Contract Lesson

| Field | Required stance |
| --- | --- |
| `primary_owner` | A new fair-mid / toxicity / side-protection owner or a lambda / congestion fee owner. |
| `allowed_consumers` | Only consumers explicitly named before source work, with actions limited to the proposed owner contract. |
| `forbidden_consumers` | Existing hazard, protection, opportunity, release, refill, recapture, calm, final quote, direct fee/base-spread, inventory, shared spread, cut, and recenter paths unless one is the explicit primary owner. |
| `failure_basin` | Oracle-shaped evidence routed into current consumers causes hidden release, overcharge, selectivity collapse, or benign-floor starvation. |
| `kill_signature` | Any screen profile with large selectivity/leakage increase, low-decile or low-retail damage, or fair-mid evidence reaching an unnamed consumer stops the branch before coefficient polish. |

### Reuse Guidance

- Admit a future proposal only if it changes the evidence owner and the consumer contract together.
- Reject proposals that copy Reference fair-mid, lambda fee, low base fee, or side-shift terms directly into the current frontier pipeline.
- Treat `ref_trade_tox_boost` as the only direct transplant with holdout evidence, but keep it scratch-only unless the current task explicitly asks for oracle-derived transplant work.
- For the next oracle-inspired batch, test owners in this order: same-step fair-mid publication throttle, lambda / congestion fee owner, stale-side protect/attract owner. Do not stack them before measuring individual owner contracts.
- Keep active-lane retained evals reserved for candidates that beat the live seed or introduce a genuinely new floor-preserving owner with materially better floor slices.

## Anchor Map Entry

Use this compact entry when updating `docs/combination_anchor_map.md`:

| Field | Value |
| --- | --- |
| `tag` | `oracle-consumer-contract-gap` |
| `signal` | Reference advantage comes from integrated fair-mid / toxicity / side-protection / congestion-fee ownership. |
| `compatibility` | Future use must redesign allowed consumers before publishing oracle-shaped evidence. |
| `collision` | Direct fair-mid, lambda, low-base, or side-shift transplants into current frontier consumers are strongly negative. |
| `kill_signature` | Hidden release, selectivity collapse, overcharge, or floor-slice damage after oracle-shaped evidence reaches an unnamed consumer. |
