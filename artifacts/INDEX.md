# Artifacts Index

## 2026-03-27

- `artifacts/code-simplifier/`: targeted hill-climb harness/test cleanup run
- `artifacts/skill-edit/`: internal doctrine capture for fail-fast contracts, migration-only compatibility, and test seam guidance

## 2026-04-01

- `artifacts/hill_climb_smoke/apr01-audit-smoke/`: retained smoke-harness lane under the current protected-surface fingerprint
- `artifacts/research/amm_dynamic_fee_apr01-screen420-2134/`: external AMM dynamic-fee evidence memo and hypothesis ranking

## 2026-04-09

- `artifacts/hill_climb/apr08-screen470-2350/`: retained coordinated hill-climb lane for the current `screen` frontier, seeded at `464.086950` mean edge and still below the `470` breakout gate

Per-run contract:

- keep only `run.json`, `state.json`, `results.jsonl`, `results.tsv`, `history.jsonl`, `hypotheses/`, `incumbents/`, and `snapshots/`
- keep the machine-readable cross-run catalog at `artifacts/index.json`
- do not recreate per-evaluation `evaluations/` trees
- do not retain old probe, compare, quarantine, or superseded baseline runs once the active lane is updated
