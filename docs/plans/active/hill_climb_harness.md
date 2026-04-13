# Hill-Climb Harness

Canonical repo-local reference:

- `docs/hill_climb_loop.md`

## Objective

Replace the old strategy-v1/v2/v3 evaluation wrappers with one agent-oriented loop:

- one active strategy source,
- one immutable evaluator against the competition normalizer,
- one scalar objective (`mean_edge`),
- one append-only artifact ledger,
- stage-specific simulation counts on fixed canonical seeds.

## Architecture

### Locked Components

These define the competition mechanics and must remain stable during research:

- Rust simulator in `amm_sim_rs/`
- baseline config and variance in `amm_competition/competition/config.py`
- match execution in `amm_competition/competition/match.py`
- validation and compilation in `amm_competition/evm/validator.py` and `amm_competition/evm/compiler.py`
- normalizer loading in `amm_competition/evm/baseline.py`

### Editable Components

- `contracts/src/Strategy.sol`

`contracts/src/candidates/` is the library of starter and archived variants. The live run path is `contracts/src/Strategy.sol`.

### Harness Components

- `amm_competition/hill_climb/stages.py`
  - defines canonical research stages
  - fixes `10000` simulation steps for every stage
  - varies only `n_simulations` and seed block
- `amm_competition/hill_climb/harness.py`
  - validates and compiles the active strategy
  - runs the stage against the competition normalizer
  - computes scorecard diagnostics
  - enforces the stage gate before incumbent replacement
  - compares `mean_edge` against the prior incumbent using a promotion margin derived from candidate and incumbent uncertainty
  - records `seed`, `keep`, `discard`, or `invalid`
- `amm_competition/cli.py`
  - exposes `hill-climb eval`, `status`, `history`, `show-eval`, `set-hypothesis`, `show-hypothesis`, `summarize-run`, `analyze-run`, `compare-profiles`, and `pull-best`

## Artifact Layout

Canonical retained runs:

- at most one active research lane under `artifacts/hill_climb/<run_id>/`
- at most one current smoke sanity lane under `artifacts/hill_climb_smoke/<run_id>/`

As of the current retained lane, the active hill-climb run is
`artifacts/hill_climb/apr12-screen480-1130/`.
Older lane `artifacts/hill_climb/apr11-screen480-0948/` is read-only history because the
protected-surface fingerprint changed; do not resume mutation there on this checkout.

The active research artifact layout is `artifacts/hill_climb/<run_id>/`.

- `run.json`: run manifest
- `state.json`: resumable run state, including optional breakout outcome gate metadata
- `results.tsv`: compact experiment ledger
- `results.jsonl`: full append-only summaries
- `incumbents/<stage>.json`: current best result for that stage
- `snapshots/<source_sha256>.sol`: deduplicated content-addressed source snapshots
- `.next_eval_index`: the only supported continuity counter

The harness no longer writes per-evaluation subfolders. Full evaluation payloads live only in
`results.jsonl`, and every record points at a shared snapshot under `snapshots/`.

Normal resume flows fail fast on stale manifests, duplicate eval IDs, missing `state.json`, or obsolete `.next_eval_id` continuity files. Retained legacy runs are unsupported in the active harness and should be replaced with fresh runs.

If a retained run fails continuity or append-only validation, do not sort or rewrite the ledgers by hand. Quarantine that run directory and continue in a fresh `run_id`.

Retention policy:

- keep one active hill-climb run under `artifacts/hill_climb/`
- keep one smoke run under `artifacts/hill_climb_smoke/`
- treat detached worker lanes and their temporary git worktrees as scratch space; once their conclusions are folded into the retained lane and plan docs, prune them
- delete probe, compare, and superseded baseline runs once their conclusions have been folded into the active lane

## Stage Ladder

- `smoke`: 8 sims on screening seeds
- `prescreen`: 12 sims on screening seeds with extra arb-leak and fee-jump guardrails for risky pivots
- `screen`: 32 sims on screening seeds
- `climb`: 128 sims on screening seeds
- `confirm`: 512 sims on holdout seeds
- `final`: 1000 sims on final-confidence seeds

## Current Operator Loop

- prefer `status --json` and `analyze-run --json` as the default read surfaces
- register active branches with `set-hypothesis` so intent coverage and recommended-next-batch analysis stay meaningful
- use `prescreen` before `screen` for risky or structural pivots
- use `compare-profiles` after any surviving `screen` candidate before spending more iterations on that line
- use `--read-only` on read surfaces when protected-surface drift should block mutation but not historical analysis

## Non-Negotiables

- No paired evals against local champion strategies.
- No moving benchmarks besides the built-in competition normalizer.
- No stage-specific changes to steps, initial reserves, or variance ranges.
- Fail fast on missing files, invalid Solidity, bad stage names, or missing incumbents.
