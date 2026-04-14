# Hill-Climb Loop Contract

This is the canonical repo-local reference for the hill-climb loop. Keep `README.md` and `program.md` short and route schema questions here.

## Active Edit Path

- The active strategy file is `contracts/src/Strategy.sol`.
- `contracts/src/StarterStrategy.sol` is the starter template; `contracts/src/Reference.sol` and `contracts/src/VanillaStrategy.sol` are read-only reference fixtures.
- `uv run amm-match hill-climb eval` only accepts `contracts/src/Strategy.sol` for normal runs.
- A run is pinned to one active strategy path in `run.json`. Normal eval flows fail fast if the run is resumed through a different source path.

## Decision Rule

Each eval makes two decisions in order:

1. Stage gate:
   - `smoke` has no minimum `mean_edge`.
   - `prescreen` requires `mean_edge >= 0.0`, `arb_loss_to_retail_gain <= 0.20`, and `max_fee_jump <= 0.0075`.
   - `screen`, `climb`, `confirm`, and `final` require `mean_edge >= 0.0`.
   - If the stage gate fails, the result is `discard`.
2. Incumbent replacement:
   - `seed`: first gate-passing result for that stage in the run.
   - `keep`: candidate `mean_edge - incumbent_mean_edge > promotion_margin`.
   - `discard`: candidate delta does not clear the promotion margin.
   - `invalid`: validation, compilation, or runtime failure.

Promotion margin:

```text
promotion_margin = max(1e-9, sqrt(candidate_se^2 + incumbent_se^2))
candidate_se = edge_stddev / sqrt(simulation_count)
```

Strictly higher `mean_edge` is not enough for noisy stages. The harness logs the raw delta, the promotion margin, and the keep/discard rationale in each summary record.

## Artifact Contract

Each run lives under `artifacts/hill_climb/<run_id>/`.

- `run.json`
  - Authoritative manifest metadata.
  - Required fields: `artifact_version`, `run_id`, `created_at`, `active_strategy_path`, `snapshot_dir`, `snapshot_layout`, `results_jsonl`, `results_tsv`, `history_path`, `hypotheses_dir`, `state_path`, `continuity_counter`.
- `state.json`
  - Authoritative resumable run state.
  - Required fields: `artifact_version`, `run_id`, `run_mode`, `current_target_stage`, `baseline_eval_id`, `incumbent_eval_ids`, `last_completed_iteration`, `stop_rules`, `next_hypothesis_id`, `next_hypothesis_note`, `updated_at`.
  - Optional field: `outcome_gate` with `{stage, minimum_mean_edge}` for explicit breakout thresholds.
- `results.jsonl`
  - Append-only full evaluation ledger.
  - Each eval now records lineage metadata: `hypothesis_id`, `parent_eval_id`, `parent_source_sha256`, `change_summary`, `research_refs`, and optional `replay_reason`.
- `results.tsv`
  - Append-only compact experiment ledger.
- `history.jsonl`
  - Derived compact read model generated from `results.jsonl`.
- `hypotheses/<hypothesis_id>.json`
  - Authoritative hypothesis registry with lifecycle, lineage, and linked eval ids.
- `incumbents/<stage>.json`
  - Derived current incumbent snapshots per stage.
- `snapshots/<source_sha256>.sol`
  - Content-addressed source snapshots shared across evaluations.
- `.next_eval_index`
  - The only supported continuity counter.

Unsupported continuity:

- `.next_eval_id` is obsolete.
- Normal eval, status, and pull-best flows fail fast if `.next_eval_id` exists, if `state.json` is missing, if eval IDs are duplicated, or if the manifest/state version is stale.
- Retained runs that still carry legacy continuity files or stale manifest/state versions are unsupported; start a fresh run instead.
- If continuity or append-only validation fails, do not hand-edit `results.jsonl`, `results.tsv`, `state.json`, or `.next_eval_index` to force a resume. Quarantine the run directory and start a fresh `run_id`.

Derived fields such as `snapshot_relpath`, `incumbent_before`, `history.jsonl`, and the compact TSV row are convenience views. If they disagree with the authoritative manifest/state/results/hypothesis contract, the run should be treated as broken and replaced with a fresh run.

## Stage Progression

- `smoke`: compile/runtime sanity and fast idea pruning.
- `prescreen`: cheap viability filter for risky pivots before the full screen block.
- `screen`: first comparable stage for baseline establishment and broad mutation search.
- `climb`: larger fixed screening block for incumbent replacement.
- `confirm`: holdout confirmation on separate seeds.
- `final`: highest-confidence local check before submission.

Promotion policy:

- Move a candidate from `screen -> climb -> confirm -> final` only after it survives the current stage as `seed` or `keep`.
- A stage failure or margin miss is a local branch failure, not a reason to overwrite the incumbent.
- If the operator is chasing a specific breakout threshold, record it with `uv run amm-match hill-climb set-state --breakout-stage <stage> --breakout-threshold <mean_edge>` and treat `keep` as local progress, not completion, until the recorded outcome gate passes.
- Use `artifacts/index.json` for machine-readable cross-run discovery, `artifacts/INDEX.md` for the human narrative, and `docs/agent_harness_guide.md` for the agent-facing read order across retained lanes and research artifacts.
- Same-stage re-evals of the same `source_sha256` fail by default. Use `--replay-reason` only for intentional replays.

## Read Surfaces

- `uv run amm-match hill-climb status`: quick incumbent/latest plus loop guidance.
- `uv run amm-match hill-climb history --run-id <id>`: compact per-eval timeline.
- `uv run amm-match hill-climb show-eval --run-id <id> --eval-id <id>`: one eval with lineage metadata.
- `uv run amm-match hill-climb set-hypothesis --run-id <id> --hypothesis-id <id> ...`: create or update the first-class hypothesis registry.
- `uv run amm-match hill-climb show-hypothesis --run-id <id> --hypothesis-id <id>`: one hypothesis with linked evals.
- `uv run amm-match hill-climb summarize-run --run-id <id>`: incumbent chain, unresolved ideas, abandoned families, and notable failures.
- `uv run amm-match hill-climb analyze-run --run-id <id>`: structured frontier bank, failure clusters, intent coverage, portfolio gaps, and recommended next-batch coverage.
- `uv run amm-match hill-climb compare-profiles --stage <stage> ...`: stage-aligned phenotype deltas for baseline, candidate, and optional anchor inputs.

Agent-facing contract:

- Prefer `--json` for all read commands and `pull-best` when another agent or harness is consuming the output.
- Keep `set-hypothesis` current for active branches; `intent_coverage`, `portfolio_gaps`, and `recommended_next_batch` are derived from the hypothesis registry, not only from raw eval history.
- Use `--read-only` on `status`, `history`, `show-eval`, `show-hypothesis`, `summarize-run`, `analyze-run`, and `compare-profiles` when protected-surface drift should block mutation but not historical analysis.
- `compare-profiles` is fail-fast: each slot must provide exactly one of `--*-eval-id` or `--*-source`, and stored evals must match the requested `--stage`.
- When a new batch is being seeded, generate ideas at the decomposition level first:
  `state estimation`, `risk budget`, `opportunity budget`, and `quote map`.
- Treat branch labels alone as insufficient evidence of diversity. A batch should cover at
  least three distinct decomposition targets, and at least one branch should be a topology
  change rather than a same-spine retune.
- Use `docs/reference_strategy_debrief.md` for the architectural benchmark and
  `docs/codex_idea_generation_prompt.md` for the batch-seeding prompt contract.

## Stop Policy

- After 3 non-improving iterations on the current line, refine the same idea with a narrower change.
- After 5 non-improving iterations, pivot to a meaningfully different hypothesis.
- If two survivors are near-replays or a full batch stays inside the same quote topology,
  force the next batch to change decomposition layer before spending more local refinements.
- After 2 failed pivots, pause and re-check the evaluator evidence before widening the search further.
- Stop when the current stage is exhausted, the next hypothesis is unclear, or the retained artifacts fail validation.
