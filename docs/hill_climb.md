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
- Pointers to operator-owned subagent and entropy guidance for search rounds.

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
Relative retained artifact roots resolve against the repository's primary checkout, so linked git worktrees still consolidate into the same canonical lane instead of minting duplicate per-worktree ledgers.
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
If a round includes several scratch probes, keep the round-local synthesis under `docs/plans/active/` and store probe sources/results outside the retained lane, for example under `artifacts/scratch_probes/<run_id>/`.
Keep `<run_id>.md` as the authoritative run index note. Split round writeups into 5-round chunk files named `docs/plans/active/<run_id>-round01-05.md`, `...-round06-10.md`, `...-round11-15.md`, and so on; the root index should list every chunk, mark the latest open span, and only add the next span once the current 5-round block closes.
Keep [`docs/combination_anchor_map.md`](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/combination_anchor_map.md) as the persistent cross-round planning surface. When a round discovers a durable positive anchor, a durable compatibility/collision rule, or a saturated failure mode that should influence future batches, append that synthesis there instead of burying it only in run-local notes.

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
5. Use `compare-profiles` and retained history to sort branches into failure basins such as `over_open_leak`, `over_tighten_clamp`, `frontier_neighbor`, and `crossover_regression`. Retire exhausted basins instead of relabeling the same spine, and add a more precise basin name when repeated evidence no longer fits the old labels.
6. Treat `max_fee_jump` as a neutral diagnostic.
7. When the search feels trapped, use web search or external literature to import missing topologies instead of relabeling the same design.
8. Prefer a fresh `run_id` when the evaluator surface changes or a retained run looks stale or corrupted.
9. Keep memo-grade probe-batch summaries outside the retained lane. `status`, `history`, and `show-eval` only summarize retained evals, not every scratch candidate you explored.
10. For long runs, chunk memo writeups every 5 rounds and keep the root `<run_id>.md` file as a stable index entrypoint.
11. Promote only durable cross-round search lessons into [`docs/combination_anchor_map.md`](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/combination_anchor_map.md); keep ephemeral round narration in the active run notes.

## Subagent Search Pattern

This is an operator convention for long strategy-search rounds, not a harness-enforced workflow.
Use it only when the user explicitly asks for parallel agents, subagents, or separate worker/reviewer help.
The main agent stays the coordinator by default: it owns synthesis, active-note updates, retained-lane decisions, harness repairs, stale-artifact cleanup, and stopping worker loops that drift from scope.
Subagents must not mutate retained ledgers, active run manifests, or cleanup paths they do not own.

For probe-heavy rounds, split roles by responsibility:

1. Topology proposer: drafts topology/interface contracts, not coefficient tweaks or renamed incumbent terms. It should use the six-layer scaffold, identify allowed and forbidden downstream consumers, state expected outcome-space movement, and include at least one outside or public-evidence-motivated idea when the local search is saturated.
2. Saturation/entropy critic: reviews the proposed batch against retained history, active run notes, and [`docs/combination_anchor_map.md`](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/combination_anchor_map.md). It should reject same-spine batches, renamed incumbent vocabulary, weak positive stacking, hidden floor-slice coupling, missing kill signatures, or any plan whose novelty is only code-space novelty.
3. Strategy worker: owns an accepted scratch implementation path. It may edit only its assigned scratch source, validate it, run `hill-climb probe`, inspect profile artifacts, and make bounded follow-up tweaks inside the accepted topology contract until the local idea is saturated.

Run the critic after the topology proposer has produced a concrete batch. The critic's job is to accept, reject, or narrow that proposed batch before any strategy worker starts source edits.

Do not spawn a coordinator subagent. Add proposer, critic, or worker roles only when they materially reduce search risk or wall time.

The topology proposer should ask itself and have clear answers for:

1. What interface contract changes, rather than what variable or coefficient changes?
2. Which layer owns the new evidence, and which downstream consumers are explicitly allowed to use it?
3. Which consumers are forbidden from seeing it so the probe has clean attribution?
4. Can the idea be described without incumbent-local vocabulary such as OOB, route/gap hazard, flow ownership, inventory overlay, burst admission, recenter release, quiet refill, or scalar hazard damping?
5. Does the batch include at least one candidate outside the incumbent vocabulary?
6. What public evidence or external mechanism motivates the topology, and what current shortfall does it target?
7. What outcome-space movement should prove the idea is real: `mean_edge`, `arb_loss_to_retail_gain`, `quote_selectivity_ratio`, `time_weighted_mean_fee`, `low_decile_mean_edge`, `low_retail_mean_edge`, or `low_volatility_mean_edge`? What range of estimates would you assign each of their expected movement?
8. What must stay near the incumbent band to make the result interpretable?
9. Is this a primary topology/interface idea or only a support control? If it is support-only, what larger primary anchor justifies it?
10. What no-op, over-open, or over-tightened result would retire the idea cleanly?

The saturation/entropy critic should follow entropy guardrails below and reject a batch when:

1. Multiple probes spend the same support signal under different labels.
2. A supposedly new idea routes evidence into similar incumbent vocabulary such as global calm, recapture eligibility, refill, inventory centering, safe-side opportunity, or broad fee-band movement without making that the explicit owned interface and a clear justification for why this time it would be different.
3. The branch stacks several sub-`0.1` positives with weak attribution.
4. Novelty depends on renamed incumbent-local terms rather than a different topology/interface contract.
5. A candidate is expected to recover one metric by sacrificing all tracked floor slices (hidden coupling issue). 
6. The batch lacks a falsifiable expected phenotype and kill signature for each probe.
7. Any other red flags that would cause entropy collapse or make the batch hard to falsify.

The critic should pressure-test likely failure modes with concrete questions before accepting a batch:

1. Which prior failure basin is this idea most likely to replay, and what profile movement would prove it did not?
2. If it claims to avoid `over_open_leak`, where is the explicit protection boundary that prevents broad fee compression or trust-gate leakage?
3. If it claims to avoid `over_tighten_clamp` or protection starvation, where is the explicit cap that preserves benign retail capture and the incumbent fee band?
4. If it is near an existing positive anchor, what is the new interface owner rather than the local coefficient or support-signal variant?
5. Which tracked floor slice is most likely to break first, and what kill threshold would stop the worker loop?
6. If none of the current basin names fit, what distinct vocabulary should the round use temporarily, and should it be promoted to [`docs/combination_anchor_map.md`](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/combination_anchor_map.md) after repeated evidence?

The strategy worker should loop only inside the accepted topology contract:

1. Write scratch source variants in owned paths and run validation before probes.
2. Use `hill-climb probe`, not retained `eval`, for local scoring.
3. Inspect score/profile artifacts after each probe and decide whether a bounded tweak is still worth testing the same idea.
4. Stop when repeated variants produce the same failure tag, exact no-op behavior, floor-slice damage, or only coefficient polish.
5. Report the best scratch source, artifact paths, profile deltas, saturation reason, and any reason the idea should or should not receive a canonical retained eval.

## Entropy Guardrails

Use these to keep long-running search loops from collapsing into the incumbent's neighborhood:

1. Keep at least one live branch away from the incumbent on more than one interface in the six-layer scaffold, not just within one local neighborhood.
2. If two discarded variants land in the same `primary_failure_tag` basin with similar profile deltas, treat that basin as exhausted and switch interfaces instead of polishing coefficients again.
3. Maintain three anchors in your reasoning: the incumbent, the best raw non-promoted branch, and one structurally different outsider (that shows the most promise for breakthrough). 
4. Write `--label` and `--description` in structural language that makes the touched interface and expected outcome-space basin obvious.
5. Periodically import outside evidence (i.e., via web search) when the loop keeps regenerating the same failure basin; do not let the harness free-run on stale internal ideas alone and entropy collapse. 

## Anti-Patterns

- Do not hand-edit `results.jsonl` or `run.json`.
- Do not persist worker-local evals under `artifacts/hill_climb/`; use `hill-climb probe` and consolidate only the chosen branch.
- Do not continue a retained run after changing protected competition mechanics; start a fresh `run_id`.
- Do not let the harness dictate idea generation. The harness should constrain evaluation quality, not design creativity.
- Do not rely on a single topology family once profile comparisons show repeated failure signatures.
- Do not spend multiple consecutive evals on same-spine fee nudges after repeated identical failure tags.
