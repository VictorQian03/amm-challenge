# Codex Idea-Generation Prompt

Use this prompt when seeding a new hypothesis batch or when the current lane looks trapped
in a local optimum.
This is for idea generation and harness planning, not direct code generation.

## Prompt Template

```text
You are not writing Solidity yet. You are generating a high-leverage hypothesis batch for
the AMM hill-climb harness.

Context:
- Active strategy: contracts/src/Strategy.sol
- Architectural reference only: contracts/src/Reference.sol
- Harness references:
  - docs/hill_climb_loop.md
  - docs/agent_harness_guide.md
  - docs/reference_strategy_debrief.md
- Current retained lane artifacts:
  - <run analysis file or analyze-run output>
  - <derived notebook findings/dead ends/search risk>
  - <hypothesis registry or current plan note>
  - <one or two representative eval/profile comparisons>

Task:
1. Describe the incumbent in four layers only:
   - state estimation
   - risk budget
   - opportunity budget
   - quote map
2. Describe the same four-layer decomposition for Reference.sol without copying its
   implementation details.
3. Identify the main local-optimum trap in the incumbent and name the hidden coupling that
   keeps recent hypotheses too similar.
4. Propose exactly 4 new hypotheses.

Hard constraints:
- Stay at the architectural and control-design level.
- Do not suggest line-by-line ports, constants, slot layouts, or implementation details.
- Do not propose "add one more overlay" ideas unless you can explain why the quote topology
  remains clean.
- Treat lower average fees alone as non-evidence; explain why any cheapening is narrowly
  gated and why it should not recreate a hidden cheap mode.
- At least 3 of the 4 hypotheses must target different primary layers.
- At least 1 hypothesis must be a true topology pivot, not a coefficient retune.
- For each hypothesis, explicitly state one layer that should remain fixed.

Output format:

## Incumbent Decomposition
- <state estimation>
- <risk budget>
- <opportunity budget>
- <quote map>

## Reference Decomposition
- <state estimation>
- <risk budget>
- <opportunity budget>
- <quote map>

## Local-Optimum Trap
- <one paragraph>

## Hypotheses
1. <short name>
   - Primary layer changed: <layer>
   - Layer held fixed: <layer>
   - Hidden coupling removed: <one sentence>
   - Core idea: <2-3 sentences>
   - Why this is structurally different: <1 sentence>
   - Expected upside: <1 sentence>
   - Expected failure signature: <1 sentence>

2. <short name>
   - Primary layer changed: <layer>
   - Layer held fixed: <layer>
   - Hidden coupling removed: <one sentence>
   - Core idea: <2-3 sentences>
   - Why this is structurally different: <1 sentence>
   - Expected upside: <1 sentence>
   - Expected failure signature: <1 sentence>

3. <short name>
   - Primary layer changed: <layer>
   - Layer held fixed: <layer>
   - Hidden coupling removed: <one sentence>
   - Core idea: <2-3 sentences>
   - Why this is structurally different: <1 sentence>
   - Expected upside: <1 sentence>
   - Expected failure signature: <1 sentence>

4. <short name>
   - Primary layer changed: <layer>
   - Layer held fixed: <layer>
   - Hidden coupling removed: <one sentence>
   - Core idea: <2-3 sentences>
   - Why this is structurally different: <1 sentence>
   - Expected upside: <1 sentence>
   - Expected failure signature: <1 sentence>

## Best Next Batch
- Recommend the first 2 hypotheses to test.
- Explain why they are the highest-leverage pair for breakout search rather than local
  refinement.
```

## Usage Notes

- Prefer feeding Codex `analyze-run --json`, one current incumbent profile, and one failed
  branch profile instead of a long narrative recap.
- Include `notebook/findings.md` or `notebook/search_risk.md` when the next batch should react
  to repeated dead ends instead of only the latest raw frontier.
- Use the latest retained lane for evidence, but start a new `run_id` if the index says the
  retained lane is historical or exhausted.
- If the last batch already contained a topology pivot, ask Codex whether it falsified the
  whole topology or only one unsafe release path.
- If the last two best survivors are near-replays, say that explicitly and require a layer
  pivot.
