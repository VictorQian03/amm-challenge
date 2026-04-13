# Artifacts Index

## 2026-03-27

- `artifacts/code-simplifier/`: targeted hill-climb harness/test cleanup run
- `artifacts/skill-edit/`: internal doctrine capture for fail-fast contracts, migration-only compatibility, and test seam guidance

## 2026-04-01

- `artifacts/hill_climb_smoke/apr01-audit-smoke/`: retained smoke-harness lane under the current protected-surface fingerprint
- `artifacts/research/amm_dynamic_fee_apr01-screen420-2134/`: external AMM dynamic-fee evidence memo and hypothesis ranking

## 2026-04-10

- `artifacts/research/amm_dynamic_fee_apr10-screen480-0931/`: source-backed worker map and outcome log for the `480`-targeted round

## 2026-04-11

- `artifacts/hill_climb/apr11-screen480-0948/`: sole retained `screen` lane after artifact hygiene cleanup; baseline `473.616393`, best raw replay `473.668925`, breakout gate still pending at `480.0`
- under the current checkout it is read-only because protected-surface drift now requires a fresh `run_id` before any further mutation/resume
- transient `apr11-screen480-0948-w0*` worker lanes and superseded retained run `apr10-screen480-0947/` were pruned after their findings were folded into the retained lane and plan docs

## 2026-04-12

- `artifacts/hill_climb/apr12-screen480-1130/`: current retained `screen` lane on the updated protected-surface fingerprint; baseline `473.616393`, breakout gate still pending at `480.0`, and `structural-pivot-two-mode-controller` is queued next
- `artifacts/research/amm_branch_portfolio_apr12-screen480-1130/`: branch portfolio memo and source log for the five-hypothesis batch that seeded the current retained lane
- `artifacts/hill_climb/apr11-screen480-0948/` remains read-only history and should not be resumed for mutation on this checkout

## 2026-04-13

- `artifacts/hill_climb/apr13-screen480-0907/`: current retained `screen` lane on the same protected-surface fingerprint; baseline `473.616393`, breakout gate still pending at `480.0`, `screen_0005` is the best raw survivor, and the seeded five-branch batch closed with no queued next hypothesis
- `artifacts/research/amm_seed_refresh_apr13-screen480-0907/`: fresh-run research memo, new-source log, and hypothesis tracker for the current retained lane
- `artifacts/hill_climb/apr12-screen480-1130/` is now read-only history for planning and should not be resumed for mutation on this checkout

Per-run contract:

- keep only `run.json`, `state.json`, `results.jsonl`, `results.tsv`, `history.jsonl`, `hypotheses/`, `incumbents/`, and `snapshots/`
- keep the machine-readable cross-run catalog at `artifacts/index.json`
- do not recreate per-evaluation `evaluations/` trees
- do not retain old probe, compare, quarantine, or superseded baseline runs once the active lane is updated
