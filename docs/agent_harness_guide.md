# Agent Harness Guide

This is the canonical agent-facing map for the current AMM harness.

## Canonical Scope

- Use this file for active-run read order, retained-lane analysis, and evidence gathering before seeding a new batch.
- Use `docs/hill_climb_loop.md` for artifact schema, stage gates, promotion rules, and stop policy.
- Use `docs/codex_idea_generation_prompt.md` for hypothesis-batch shape, entropy, and anti-replay constraints.

## Start Here

- Use `uv run amm-match ...` for repo-local commands. Do not rely on a globally installed `amm-match` binary or an activated virtualenv.
- The only mutable strategy file is `contracts/src/Strategy.sol`.
- `contracts/src/StarterStrategy.sol` is the starter template.
- `contracts/src/Reference.sol` is a protected benchmark source. Do not open, read, diff, summarize, or compare against it unless the user explicitly authorizes that file access in the current turn.
- `contracts/src/VanillaStrategy.sol` is the fixed-fee normalizer fixture.
- For new batches, jump directly to `docs/codex_idea_generation_prompt.md`.

## Fresh-Run State

- The repo is parked on baseline `contracts/src/Strategy.sol`.
- Treat retained lanes as read surfaces unless `artifacts/index.json` explicitly marks one
  as active.
- If the latest retained lane is historical, exhausted, or fingerprint-stale, start a new
  `run_id` instead of resuming.

## Active Loop

Default read surfaces:

- `uv run amm-match hill-climb status --run-id <id> --stage <stage> --json`
- `uv run amm-match hill-climb analyze-run --run-id <id> --json`
- `uv run amm-match hill-climb show-hypothesis --run-id <id> --hypothesis-id <id> --json`
- `uv run amm-match hill-climb compare-profiles --run-id <id> --stage <stage> --baseline-eval-id <id> --candidate-eval-id <id> --json`

Write surfaces:

- `uv run amm-match hill-climb eval contracts/src/Strategy.sol --run-id <id> --stage <stage> ...`
- `uv run amm-match hill-climb set-hypothesis --run-id <id> --hypothesis-id <id> ...`
- `uv run amm-match hill-climb set-state --run-id <id> ...`
- `uv run amm-match hill-climb pull-best --run-id <id> --stage <stage> --destination contracts/src/Strategy.sol`

Fail-fast rules:

- normal eval only accepts `contracts/src/Strategy.sol`
- historical read commands support `--read-only` when protected-surface drift blocks mutation
- do not hand-edit `results.jsonl`, `results.tsv`, `state.json`, or `.next_eval_index`

## Cross-Run Discovery

Use these in order:

1. `artifacts/index.json`
2. `artifacts/INDEX.md`
3. `docs/hill_climb_loop.md`

Interpretation:

- `artifacts/index.json` is the machine-readable cross-run catalog. Use it first for agent automation.
- `artifacts/INDEX.md` is the human narrative for which lane is current, which lanes are historical, and what research artifacts go with them.
- `docs/hill_climb_loop.md` defines the retained-run schema and the read/write contract.
- Closed-lane narratives live under `docs/plans/completed/`; `docs/plans/active/` should only hold the truly active plan note plus stable historical redirect targets referenced by older ledgers.

## Retained Run Read Order

For one run under `artifacts/hill_climb/<run_id>/`:

1. `uv run amm-match hill-climb status --run-id <id> --stage <stage> --json`
2. `uv run amm-match hill-climb analyze-run --run-id <id> --json`
3. `run.json`
4. `state.json`
5. `notebook/search_risk.md`
6. `notebook/findings.md`
7. `notebook/dead_ends.md`
8. `history.jsonl`
9. `hypotheses/`
10. `results.jsonl`

Notes:

- prefer the CLI read surfaces over reading raw ledgers first
- `analysis.json` is a cached convenience artifact, not the contract
- `notebook/*.md` is also derived convenience output rebuilt from canonical ledgers
- historical lanes are for planning unless the current checkout still matches their protected-surface fingerprint

## Research Artifact Read Order

For one directory under `artifacts/research/<topic>/`, read the core files that exist in
this order:

1. `memo.md`
2. `hypothesis_log.md`
3. `sources.json`
4. `run_config.json`
5. `experiment_registry.json`

Optional supporting trace files, when present:

1. `verification.md`
2. `eda_report.md`
3. `context_log.md`
4. `commands.log`
5. `CHANGELOG.md`

Interpretation:

- older retained bundles may stop at `memo.md`, `hypothesis_log.md`, and `sources.json`
- `memo.md` is the shortest synthesis of conclusions and recommended next move
- `hypothesis_log.md` and `experiment_registry.json` capture branch inventory and status
- `run_config.json`, when present, states the question, constraints, and breakout target
- `sources.json` and `verification.md` back the memo with evidence
- the remaining files are supporting trace artifacts

## Idea-Generation Inputs

When seeding a fresh batch or escaping a local optimum, gather:

- `uv run amm-match hill-climb analyze-run --run-id <id> --json`
- `uv run amm-match hill-climb show-hypothesis --run-id <id> --hypothesis-id <id> --json` for each recent non-promoted branch you might replay, rename, or supersede
- one incumbent profile and one failed-branch profile from `compare-profiles`
- `artifacts/hill_climb/<run_id>/notebook/search_risk.md`
- `artifacts/hill_climb/<run_id>/notebook/findings.md`
- the linked research memo under `artifacts/research/<topic>/memo.md`
- `docs/codex_idea_generation_prompt.md`

Prefer architectural hypotheses over line edits. The prompt contract assumes the four-layer decomposition used by the retained-run analysis surfaces.
Treat `portfolio_bank` as the preferred screen-stage planning anchor surface when multiple structurally distinct near-frontier strategies exist. When you intentionally branch from one of those anchors, carry the reused eval id into the new hypothesis through `nearest_prior_successes`.
Before you name or queue a new branch, describe both the official incumbent and the strongest raw survivor in fair-mid terms: what latent or fair mid they estimate, how quickly it updates, when it recenters, and how divergence from that estimate is turned into protection or relief.
When a branch changes `state`, reflect that fair-mid semantics directly in the title, label, and rationale instead of using only generic words like `toxic`, `state`, or `filter`.
For fresh idea generation, prefer at least two targeted web searches for outside statistical, market-making, inventory-control, adverse-selection, or microstructure ideas that are absent from the retained lane. Record the concept in `novelty_coordinates.external_idea` and the supporting file or URL in `research_refs`.

Use the derived benchmark debrief to calibrate the screening language. As of
`2026-04-16`, the protected benchmark phenotype was locally stronger than the incumbent on
both `prescreen` and `screen` even though its `max_fee_jump` was higher, so raw jump size
is not a safe hard proxy for architectural quality.

Do not seed a batch from labels alone. Read these `analyze-run --json` surfaces explicitly:

- `batch_diversity.quote_topology_groups`
- `batch_diversity.repeated_quote_topology_groups`
- `batch_diversity.phenotype_family_groups`
- `batch_diversity.repeated_phenotype_family_groups`
- `batch_diversity.same_spine_failure_groups`
- `batch_diversity.same_phenotype_failure_groups`
- `portfolio_bank`
- `phenotype_coverage`
- `failure_clusters`

If you cannot point to one recent `compare-profiles` read and one recent hypothesis payload that the new idea is reacting to, the batch is under-evidenced.

For topology diversity, neutral naming, anti-replay checks, and held-fixed-layer rules, use
`docs/codex_idea_generation_prompt.md` as the canonical batch-shaping contract.
