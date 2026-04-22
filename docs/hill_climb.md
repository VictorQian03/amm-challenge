# Thin Hill-Climb Harness

This harness is intentionally narrow.
It owns evaluation discipline, retained run ledgers, and anti-regression guardrails.
It does not own idea generation, batch planning, or hypothesis workflow.

## What It Covers

- Fixed stage presets with canonical seed blocks.
- Consolidated retained ledgers under `artifacts/hill_climb/<run_id>/`.
- Content-addressed source snapshots so repeated restores do not regenerate duplicate artifacts.
- Derived incumbent, best-raw, and history read surfaces without per-run duplicate files.
- Protected-mechanics fingerprinting so a retained run does not silently span evaluator changes.

## What It Does Not Cover

- No required hypothesis registry.
- No batch-diversity contract.
- No idea-generation queue or structured planning state.
- No forced refine or pivot workflow.

Agents should use the harness to measure and compare candidates, not to decide how to search.

## Run Layout

Each run lives under `artifacts/hill_climb/<run_id>/`.

- `run.json`: minimal manifest for the retained lane, protected-surface fingerprint, and eval/snapshot counts.
- `results.jsonl`: authoritative append-only eval ledger.
- `snapshots/<sha256>.sol`: content-addressed source snapshots.

Cross-run navigation lives at `artifacts/hill_climb/index.json`.
The newest valid run is marked `active`; older valid runs are `historical`; fingerprint-stale or corrupted runs are `blocked`.
The run layout is canonical: retained lanes may keep only `run.json`, `results.jsonl`, and referenced snapshots.
`status`, `history`, incumbents, and best-raw views are rebuilt from `results.jsonl` instead of being persisted as extra files.
Legacy per-run files such as `results.tsv`, `history.jsonl`, `incumbents/`, or `.next_eval_index` are treated as invalid retained state.

## Commands

Run a retained eval:

```bash
uv run amm-match hill-climb eval --run-id apr21 --stage screen
```

On a fresh run, the first passing eval at a stage becomes that stage's incumbent.
The default eval source is `contracts/src/StarterStrategy.sol`, so `screen_0001` is the canonical way to seed the local incumbent from the current starter strategy.

Run a scratch probe in a worker worktree without creating retained artifacts:

```bash
uv run amm-match hill-climb probe --stage screen contracts/src/StarterStrategy.sol
```

Use `probe` for branch scouting and rerun only the chosen branch into the canonical retained lane with `hill-climb eval`.
The thin harness does not have an `analyze-run` command, queued-hypothesis surface, or built-in batch-diversity report.
If a round includes several scratch probes, keep the synthesis in an active plan note under `docs/plans/active/` and store probe sources/results outside the retained lane, for example under `artifacts/scratch_probes/<run_id>/`.

List runs:

```bash
uv run amm-match hill-climb runs
```

Inspect one run:

```bash
uv run amm-match hill-climb status --run-id apr21
uv run amm-match hill-climb history --run-id apr21
uv run amm-match hill-climb show-eval --run-id apr21 --eval-id screen_0004
```

Restore the current incumbent:

```bash
uv run amm-match hill-climb pull-best --run-id apr21 --stage screen --destination contracts/src/StarterStrategy.sol
```

Compare phenotype/profile deltas:

```bash
uv run amm-match hill-climb compare-profiles \
  --stage screen \
  --run-id apr21 \
  --baseline-eval-id screen_0002 \
  --candidate-source contracts/src/StarterStrategy.sol
```

`compare-profiles` with a `--*-source` argument still runs the evaluator.
If protected competition mechanics are dirty, it blocks for the same reason a retained eval would block.

## Persistence Guardrails

1. `artifacts/hill_climb/<run_id>/` is for canonical retained lanes only.
2. Worker-local exploration belongs in worktrees via `hill-climb probe`, not as extra retained `run_id`s.
3. Only selected branches should be rerun into the canonical retained lane with `hill-climb eval`.
4. Retained lanes stay compact on purpose: no per-run TSV mirror, no persisted history mirror, no persisted incumbent mirror, and no worker scratch directories under the retained root.

## Stage Discipline

- `smoke`: quick runtime sanity check.
- `prescreen`: cheap risky-pivot filter; rejects materially arb-leaky candidates.
- `screen`: canonical fixed-seed screening stage.
- `climb`: larger screening block for stronger incumbent replacement.
- `confirm`: disjoint holdout confirmation.
- `final`: largest local confidence run.

Replacement rule:

1. Candidate must pass the stage gate.
2. If there is no incumbent for that stage, the result is `seed`.
3. Otherwise, it becomes `keep` only if `mean_edge - incumbent_mean_edge` clears the promotion margin.

Promotion margin:

```text
promotion_margin = max(1e-9, sqrt(candidate_se^2 + incumbent_se^2))
candidate_se = edge_stddev / sqrt(simulation_count)
```

This keeps the harness strict on measurement without prescribing what the next search step should be.

## Search Guidance

Use these as search prompts, not as required workflow:

1. Use the six-layer scaffold `observation shaping -> latent state -> hazard/calm classifier -> shared spread -> side-specific protection -> safe-side recapture/opportunity`.
2. Hold the scaffold fixed, mutate one interface at a time, and favor explicit interface separation with a factorized causal representation instead of a coupled pipeline rewrite.
3. Keep an explicit explore/exploit split. Do not spend every iteration on local coefficient polish.
4. Judge novelty in outcome-space, not code-space. Branch diversity is about expected movement in `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, and floor slices, not about mechanism names.
5. Use `compare-profiles` and retained history to sort branches into failure basins such as `over_open_leak`, `over_tighten_clamp`, `frontier_neighbor`, and `crossover_regression`. Retire exhausted basins instead of relabeling the same spine.
6. Treat `max_fee_jump` as a neutral diagnostic. It is often informative and sometimes higher in better branches, so do not use it as a blanket smoothing target.
7. When the search feels trapped, use web search or external literature to import missing topologies instead of relabeling the same design.
8. Prefer a fresh `run_id` when the evaluator surface changes or a retained run looks stale or corrupted.
9. Keep memo-grade probe-batch summaries outside the retained lane. `status`, `history`, and `show-eval` only summarize retained evals, not every scratch candidate you explored.

## Entropy Guardrails

Use these to keep long-running search loops from collapsing into the incumbent's neighborhood:

1. Keep at least one live branch away from the incumbent on more than one interface in the six-layer scaffold, not just within one local neighborhood.
2. If two discarded variants land in the same `primary_failure_tag` basin with similar profile deltas, treat that basin as exhausted and switch interfaces instead of polishing coefficients again.
3. Maintain three anchors in your reasoning: the incumbent, the best raw non-promoted branch, and one structurally different outsider.
4. Write `--label` and `--description` in structural language that makes the touched interface and expected outcome-space basin obvious.
5. Periodically import outside evidence when the loop keeps regenerating the same failure basin; do not let the harness free-run on stale internal ideas alone.

## Anti-Patterns

- Do not hand-edit `results.jsonl` or `run.json`.
- Do not persist worker-local evals under `artifacts/hill_climb/`; use `hill-climb probe` and consolidate only the chosen branch.
- Do not continue a retained run after changing protected competition mechanics; start a fresh `run_id`.
- Do not let the harness dictate idea generation. The harness should constrain evaluation quality, not design creativity.
- Do not rely on a single topology family once profile comparisons show repeated failure signatures.
- Do not spend multiple consecutive evals on same-spine fee nudges after repeated identical failure tags.
