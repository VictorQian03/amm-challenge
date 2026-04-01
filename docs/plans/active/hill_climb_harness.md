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
  - exposes `hill-climb eval`, `hill-climb status`, and `hill-climb pull-best`

## Artifact Layout

Canonical retained runs:

- at most one active research lane under `artifacts/hill_climb/<run_id>/`
- at most one current smoke sanity lane under `artifacts/hill_climb_smoke/<run_id>/`

As of the latest artifact hygiene cleanup, there is no retained active research lane. Start a fresh `run_id` before resuming hill climbing.

The active research artifact layout is `artifacts/hill_climb/<run_id>/`.

- `run.json`: run manifest
- `state.json`: resumable run state
- `results.tsv`: compact experiment ledger
- `results.jsonl`: full append-only summaries
- `incumbents/<stage>.json`: current best result for that stage
- `snapshots/<source_sha256>.sol`: deduplicated content-addressed source snapshots
- `.next_eval_index`: the only supported continuity counter

The harness no longer writes per-evaluation subfolders. Full evaluation payloads live only in
`results.jsonl`, and every record points at a shared snapshot under `snapshots/`.

Normal resume flows fail fast on stale manifests, duplicate eval IDs, missing `state.json`, or obsolete `.next_eval_id` continuity files. Retained legacy runs are unsupported in the active harness and should be replaced with fresh runs.

Retention policy:

- keep one active hill-climb run under `artifacts/hill_climb/`
- keep one smoke run under `artifacts/hill_climb_smoke/`
- delete probe, compare, and superseded baseline runs once their conclusions have been folded into the active lane

Legacy runs can be normalized with:

## Stage Ladder

- `smoke`: 8 sims on screening seeds
- `screen`: 32 sims on screening seeds
- `climb`: 128 sims on screening seeds
- `confirm`: 512 sims on holdout seeds
- `final`: 1000 sims on final-confidence seeds

## Non-Negotiables

- No paired evals against local champion strategies.
- No moving benchmarks besides the built-in competition normalizer.
- No stage-specific changes to steps, initial reserves, or variance ranges.
- Fail fast on missing files, invalid Solidity, bad stage names, or missing incumbents.
