# Agent Harness Guide

This is the canonical agent-facing map for the current AMM harness.

## Start Here

- Use `uv run amm-match ...` for repo-local commands. Do not rely on a globally installed `amm-match` binary or an activated virtualenv.
- The only mutable strategy file is `contracts/src/Strategy.sol`.
- `contracts/src/StarterStrategy.sol` is the starter template.
- `contracts/src/Reference.sol` is an architectural benchmark, not a porting target.
- `contracts/src/VanillaStrategy.sol` is the fixed-fee normalizer fixture.
- Use `docs/reference_strategy_debrief.md` when generating new batches.

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
- one incumbent profile and one failed-branch profile from `compare-profiles`
- `artifacts/hill_climb/<run_id>/notebook/search_risk.md`
- `artifacts/hill_climb/<run_id>/notebook/findings.md`
- the linked research memo under `artifacts/research/<topic>/memo.md`
- `docs/reference_strategy_debrief.md`
- `docs/codex_idea_generation_prompt.md`

Prefer architectural hypotheses over line edits. The prompt contract assumes the four-layer decomposition used by the retained-run analysis surfaces.
