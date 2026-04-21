# Codex Idea-Generation Prompt

Use this prompt when seeding a new hypothesis batch or when the current lane looks trapped
in a local optimum.
This is for idea generation and harness planning, not direct code generation.

## Canonical Scope

- Use this file for batch-generation constraints, entropy rules, anti-replay checks, and required output format.
- Use `docs/agent_harness_guide.md` to gather the retained-run evidence before invoking this prompt.
- Use `docs/hill_climb_loop.md` for stage gates and harness contract details.

## Prompt Template

```text
You are not writing Solidity yet. You are generating a high-leverage hypothesis batch for
the AMM hill-climb harness.

Context:
- Active strategy: contracts/src/Strategy.sol
- Harness references:
  - docs/hill_climb_loop.md
  - docs/agent_harness_guide.md
- Current retained lane artifacts:
  - <run analysis file or analyze-run output, including batch_diversity, phenotype_coverage, and portfolio_bank>
  - <derived notebook findings/dead ends/search risk>
  - <hypothesis registry or current plan note>
  - <one or two recent hypothesis json payloads from the exhausted batch>
  - <one or two representative eval/profile comparisons>

If the retained lane exposes a non-empty `portfolio_bank`, treat it as the preferred list
of structurally distinct screen-stage anchors before you fall back to only the official
incumbent. When you intentionally reuse one of those anchors in a new hypothesis, plan to
record its eval id through the hypothesis field `nearest_prior_successes`.
Before drafting hypotheses, restate both the official incumbent and the strongest raw survivor in fair-mid terms: what latent or fair mid is being estimated, how it updates, when it recenters, and how quote logic uses the gap between spot and fair mid.
If web access is available, do targeted web searches before finalizing the batch unless the retained evidence already spans the missing layer or topology space. Prefer outside concepts that are absent from the exhausted batch, and plan to carry them into the eventual hypothesis records through `novelty_coordinates.external_idea` plus `research_refs`.

Task:
1. Describe the incumbent in four layers only:
   - state estimation
   - risk budget
   - opportunity budget
   - quote map
2. Describe the target benchmark phenotype in the same four-layer decomposition using only
   the derived benchmark debrief and retained comparison findings.
3. Identify the main local-optimum trap in the incumbent and name the hidden coupling that
   keeps recent hypotheses too similar.
4. Diagnose whether the search failure is primarily:
   - phenotype collapse
   - decomposition-label collapse
   - screening-metric collapse
   - missing evidence from the harness inputs
   - or a combination
5. Propose exactly 4 new hypotheses.

Hard constraints:
- Stay at the architectural and control-design level.
- Treat `state estimation` as fair-mid estimation first, not as a vague bucket. Name the latent or fair mid, its update rule, its recenter rule, and how divergence from that estimate changes quoting.
- Do not suggest line-by-line ports, constants, slot layouts, or implementation details.
- Do not propose "add one more overlay" ideas unless you can explain why the quote topology
  remains clean.
- Treat lower average fees alone as non-evidence; explain why any cheapening is narrowly
  gated and why it should not recreate a hidden cheap mode.
- Treat `max_fee_jump` as diagnostic context, not a hard proxy for quality. Use
  `time_weighted_mean_fee`, `arb_loss_to_retail_gain`, and `quote_selectivity_ratio`
  before concluding that a higher-motion branch is invalid.
- At least 3 of the 4 hypotheses must target different primary layers.
- At least 1 hypothesis must be a true topology pivot, not a coefficient retune.
- Layer labels are not enough. Diversify `quote_topology`, `mutation_family`, and
  `novelty_coordinates.external_idea`, not only `primary_layer_changed`.
- At most 1 hypothesis may reuse a `quote_topology` named in
  `repeated_quote_topology_groups` or `same_spine_failure_groups`, unless it is an explicit
  falsification-control branch.
- At most 2 hypotheses may remain inside the same coarse `phenotype_family`, and only if
  they isolate different layers.
- At least 2 hypotheses must introduce a `quote_topology` and
  `novelty_coordinates.external_idea` pair that was absent from the most recent exhausted
  batch.
- Prefer at least 2 hypotheses whose `novelty_coordinates.external_idea` came from explicit web searches rather than only from relabeling local evidence. If you skip web search, say why the retained evidence already covers the missing fair-mid or topology space.
- At least 1 hypothesis must change state semantics or quote assembly rather than proposing
  another floor / release / envelope / latch controller on the same additive surface.
- Use neutral, high-level labels. Prefer `single-surface additive`,
  `baseline-plus-side-specific protection`, `two-channel quote assembly`, and
  `regime-switched quote assembly` over incumbent-shaped labels like `shared-floor-*` or
  controller-shaped labels like `credit-envelope`, `latch`, or `defensive-core-router`.
- If the branch changes state estimation, make the label and title mention the fair-mid semantic change, such as persistence, recentering, anchoring, or divergence handling.
- For every hypothesis, name the anti-target phenotype that would prove it is still a replay.
- For each hypothesis, explicitly state one layer that should remain fixed.

Output format:

## Incumbent Decomposition
- <state estimation>
- <risk budget>
- <opportunity budget>
- <quote map>

## Benchmark Decomposition
- <state estimation>
- <risk budget>
- <opportunity budget>
- <quote map>

## Local-Optimum Trap
- <one paragraph>

## Failure Diagnosis
- <one paragraph on whether this is phenotype collapse, decomposition collapse, evidence gap, or mixed>

## Hypotheses
1. <short name>
   - Primary layer changed: <layer>
   - Layer held fixed: <layer>
   - Fair-mid implication: <one sentence on how the latent/fair mid estimate changes or stays fixed>
   - Quote topology: <topology label>
   - Phenotype family: <coarse family such as shared-surface quote control or multi-channel quote assembly>
   - Mutation family: <family label>
   - Novelty coordinates: <json-like short object>
   - External research hook: <web-searched concept, paper idea, or domain phrase>
   - Hidden coupling removed: <one sentence>
   - Evidence anchor: <which prior failure / compare-profile this reacts to>
   - Anti-target phenotype: <one sentence>
   - Core idea: <2-3 sentences>
   - Why this is structurally different: <1 sentence>
   - Expected upside: <1 sentence>
   - Expected failure signature: <1 sentence>

2. <short name>
   - Primary layer changed: <layer>
   - Layer held fixed: <layer>
   - Fair-mid implication: <one sentence on how the latent/fair mid estimate changes or stays fixed>
   - Quote topology: <topology label>
   - Phenotype family: <coarse family such as shared-surface quote control or multi-channel quote assembly>
   - Mutation family: <family label>
   - Novelty coordinates: <json-like short object>
   - External research hook: <web-searched concept, paper idea, or domain phrase>
   - Hidden coupling removed: <one sentence>
   - Evidence anchor: <which prior failure / compare-profile this reacts to>
   - Anti-target phenotype: <one sentence>
   - Core idea: <2-3 sentences>
   - Why this is structurally different: <1 sentence>
   - Expected upside: <1 sentence>
   - Expected failure signature: <1 sentence>

3. <short name>
   - Primary layer changed: <layer>
   - Layer held fixed: <layer>
   - Fair-mid implication: <one sentence on how the latent/fair mid estimate changes or stays fixed>
   - Quote topology: <topology label>
   - Phenotype family: <coarse family such as shared-surface quote control or multi-channel quote assembly>
   - Mutation family: <family label>
   - Novelty coordinates: <json-like short object>
   - External research hook: <web-searched concept, paper idea, or domain phrase>
   - Hidden coupling removed: <one sentence>
   - Evidence anchor: <which prior failure / compare-profile this reacts to>
   - Anti-target phenotype: <one sentence>
   - Core idea: <2-3 sentences>
   - Why this is structurally different: <1 sentence>
   - Expected upside: <1 sentence>
   - Expected failure signature: <1 sentence>

4. <short name>
   - Primary layer changed: <layer>
   - Layer held fixed: <layer>
   - Fair-mid implication: <one sentence on how the latent/fair mid estimate changes or stays fixed>
   - Quote topology: <topology label>
   - Phenotype family: <coarse family such as shared-surface quote control or multi-channel quote assembly>
   - Mutation family: <family label>
   - Novelty coordinates: <json-like short object>
   - External research hook: <web-searched concept, paper idea, or domain phrase>
   - Hidden coupling removed: <one sentence>
   - Evidence anchor: <which prior failure / compare-profile this reacts to>
   - Anti-target phenotype: <one sentence>
   - Core idea: <2-3 sentences>
   - Why this is structurally different: <1 sentence>
   - Expected upside: <1 sentence>
   - Expected failure signature: <1 sentence>

## Entropy Check
- Reused quote topologies: <list or none>
- Reused phenotype families: <list or none>
- New quote topologies vs exhausted batch: <list>
- New external ideas vs exhausted batch: <list>
- Web-searched external ideas: <list or explain why web search was skipped>
- Why this batch should not collapse into one phenotype: <2-3 sentences>

## Best Next Batch
- Recommend the first 2 hypotheses to test.
- Explain why they are the highest-leverage pair for breakout search rather than local
  refinement.
```
