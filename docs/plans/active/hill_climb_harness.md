# Hill-Climb Harness

Minimal routing note for the hill-climb workflow.

Canonical references:

- `docs/hill_climb_loop.md`
- `docs/agent_harness_guide.md`
- `program.md`

## Core Contract

- mutate only `contracts/src/Strategy.sol`
- keep the competition evaluator fixed
- optimize `mean_edge`
- use append-only retained artifacts
- vary only `n_simulations` and seed block by stage

## Operator Loop

- read first:
  - `uv run amm-match hill-climb status --run-id <id> --stage <stage> --json`
  - `uv run amm-match hill-climb analyze-run --run-id <id> --json`
- use the derived notebook surfaces when seeding a fresh batch from history:
  - `artifacts/hill_climb/<run_id>/notebook/findings.md`
  - `artifacts/hill_climb/<run_id>/notebook/search_risk.md`
- register active branches with `set-hypothesis`
- risky or structural pivots: `prescreen` before `screen`
- local refinements: start at `screen`
- after any surviving `screen` candidate, use `compare-profiles`
- after a `discard` or `invalid`, restore with `pull-best`

## Stages

- `smoke`: 8 sims
- `prescreen`: 12 sims with extra arb-leak and fee-jump guardrails
- `screen`: 32 sims
- `climb`: 128 sims
- `confirm`: 512 sims
- `final`: 1000 sims

Every stage uses the fixed competition-length run from the evaluator.

## Fresh-Run Rule

- resolve lane state through `artifacts/index.json` first
- if no lane is marked active, start a fresh `run_id`
- if a retained lane is stale, historical, or broken, read it with `--read-only` and do not
  resume mutation
- never hand-edit run ledgers or continuity files
