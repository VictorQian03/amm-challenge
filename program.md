# AMM Hill-Climb Program

This repo now uses a single-file hill-climbing loop for strategy research.

## Locked Surface

- Do not modify the competition mechanics or evaluator:
  - `amm_sim_rs/`
  - `amm_competition/competition/config.py`
  - `amm_competition/competition/match.py`
  - `amm_competition/evm/baseline.py`
  - `amm_competition/evm/compiler.py`
  - `amm_competition/evm/validator.py`
- Do not add paired evals against local champion strategies.
- The objective is `mean_edge` on fixed canonical seeds against the competition normalizer.

## Editable Surface

- `contracts/src/Strategy.sol`

Keep this file reviewable. Prefer small, explicit mutations over broad rewrites unless the current design is exhausted. Treat `contracts/src/candidates/` as the library of starter and archived variants, not the live run path.

## Research Loop

1. Read `README.md`, this file, and `contracts/src/Strategy.sol`.
2. Pick a `run_id` such as `mar26`.
3. Establish the baseline first:
   - `uv run amm-match hill-climb eval contracts/src/Strategy.sol --run-id mar26 --stage screen --label baseline`
4. For each new idea:
   - edit `contracts/src/Strategy.sol`
   - run `uv run amm-match hill-climb eval contracts/src/Strategy.sol --run-id mar26 --stage screen --label <short-label> --description "<what changed>"`
   - if status is `discard`, restore the incumbent before the next idea:
     - `uv run amm-match hill-climb pull-best --run-id mar26 --stage screen`
5. Inspect current state at any time:
   - `uv run amm-match hill-climb status --run-id mar26 --stage screen`
6. Promote surviving ideas through higher-simulation stages:
   - `screen` -> `climb` -> `confirm` -> `final`

See `docs/hill_climb_loop.md` for the canonical artifact schema, stage progression policy, and stop rules.

## Stage Contract

- Every stage uses full competition-length simulations (`10000` steps).
- Only `n_simulations` changes by stage.
- Stages use explicit canonical seed blocks so results are comparable within a stage.

## Decision Rule

- `seed`: first gate-passing result for the stage in this run.
- `keep`: candidate `mean_edge - incumbent_mean_edge` clears the promotion margin derived from candidate and incumbent uncertainty.
- `discard`: stage gate failure, or delta does not clear the promotion margin.
- `invalid`: validation, compilation, or runtime failure.

Strictly higher `mean_edge` is not enough on noisy stages.
