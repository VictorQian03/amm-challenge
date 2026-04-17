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

Keep this file reviewable. Prefer the smallest change that tests a distinct architectural
thesis, not merely the smallest coefficient change. `contracts/src/StarterStrategy.sol`
is the starter template, while `contracts/src/Reference.sol` and
`contracts/src/VanillaStrategy.sol` are read-only fixtures. After near-replay survivors or
same-spine failures, pivot decomposition layer or quote topology instead of doing another
coefficient retune. Use `docs/reference_strategy_debrief.md`,
`docs/codex_idea_generation_prompt.md`, and `docs/agent_harness_guide.md` when seeding a
new batch or reasoning from retained artifacts.

## Research Loop

1. Read `README.md`, this file, and `contracts/src/Strategy.sol`.
2. Pick a `run_id` such as `mar26`.
3. Establish the baseline first:
   - `uv run amm-match hill-climb eval contracts/src/Strategy.sol --run-id mar26 --stage screen --label baseline`
4. Before each new branch:
   - inspect the retained run in machine-readable form:
     - `uv run amm-match hill-climb analyze-run --run-id mar26 --json`
     - `uv run amm-match hill-climb status --run-id mar26 --stage screen --json`
   - if seeding a fresh batch or escaping a local optimum, use
     `docs/codex_idea_generation_prompt.md` against the retained run evidence before coding
   - register or update the branch with `set-hypothesis` so intent coverage, portfolio gaps, and recommended-next-batch planning stay meaningful:
     - `uv run amm-match hill-climb set-hypothesis --run-id mar26 --hypothesis-id anti-arb-01 --title "Anti-arb branch" --rationale "Reduce toxic-flow leakage without blowing out calm-flow fees" --expected-effect "Improve arb discipline while preserving screen mean_edge" --mutation-family anti-arb --target-metrics arb_loss_to_retail_gain=-0.03 --hard-guardrails max_fee_jump=0.005 --expected-failure-mode arb_leak_regression`
5. For each new idea:
   - edit `contracts/src/Strategy.sol`
   - run `uv run amm-match hill-climb eval contracts/src/Strategy.sol --run-id mar26 --stage prescreen --label <short-label> --description "<what changed>"` for risky pivots
   - run `uv run amm-match hill-climb eval contracts/src/Strategy.sol --run-id mar26 --stage screen --label <short-label> --description "<what changed>"` once the shape survives or if the change is already local and low-risk
   - after any surviving `screen` candidate, compare it against the current screen incumbent before continuing that line:
     - `uv run amm-match hill-climb compare-profiles --run-id mar26 --stage screen --baseline-eval-id screen_0001 --candidate-eval-id screen_0002 --json`
   - if status is `discard` or `invalid`, restore the incumbent before the next idea:
     - `uv run amm-match hill-climb pull-best --run-id mar26 --stage screen`
6. Inspect current state at any time:
   - `uv run amm-match hill-climb status --run-id mar26 --stage screen --json`
   - `uv run amm-match hill-climb analyze-run --run-id mar26 --json`
   - `uv run amm-match hill-climb compare-profiles --run-id mar26 --stage screen --baseline-eval-id screen_0001 --candidate-eval-id screen_0002`
   - `uv run amm-match hill-climb show-hypothesis --run-id mar26 --hypothesis-id anti-arb-01 --json`
   - If the user asked for a specific breakout threshold, record it once:
     - `uv run amm-match hill-climb set-state --run-id mar26 --breakout-stage screen --breakout-threshold 424`
7. Promote surviving ideas through higher-simulation stages:
   - `screen` -> `climb` -> `confirm` -> `final`

See `docs/hill_climb_loop.md` for the canonical artifact schema, stage progression policy, and stop rules.
See `docs/agent_harness_guide.md` for the fastest read order across CLI, retained lanes, historical evals, and research memos.

## Stage Contract

- Every stage uses full competition-length simulations (`10000` steps).
- Only `n_simulations` changes by stage.
- Stages use explicit canonical seed blocks so results are comparable within a stage.
- `prescreen` is the fail-fast gate for risky pivots and rejects obvious arb-leak or fee-spike shapes before a full `screen` spend.

## Decision Rule

- `seed`: first gate-passing result for the stage in this run.
- `keep`: candidate `mean_edge - incumbent_mean_edge` clears the promotion margin derived from candidate and incumbent uncertainty.
- `discard`: stage gate failure, or delta does not clear the promotion margin.
- `invalid`: validation, compilation, or runtime failure.

Strictly higher `mean_edge` is not enough on noisy stages.

## Agent Read Surface

- Prefer `--json` for agent automation on `status`, `history`, `show-eval`, `show-hypothesis`, `summarize-run`, `analyze-run`, `compare-profiles`, and `pull-best`.
- Keep hypothesis records current with `set-hypothesis`; otherwise decomposition coverage, batch-diversity checks, structural recommendations, `intent_coverage`, `portfolio_gaps`, family/layer risk scoreboards, and `recommended_next_batch` are incomplete planning signals.
- Use `analyze-run` to inspect failure clusters, layer/topology diversity, intent coverage, portfolio gaps, notebook-style findings/dead ends, and the recommended next-batch scaffold before proposing workers.
- Use `artifacts/hill_climb/<run_id>/notebook/` only as a cached convenience surface. The canonical source of truth remains `results.jsonl`, `state.json`, and `hypotheses/`.
- Use `--read-only` on analysis commands when protected-surface drift blocks normal mutation flows but historical reasoning is still needed.

If a retained run fails continuity or append-only validation, do not repair the ledgers by hand. Quarantine that run and start a fresh `run_id`.
