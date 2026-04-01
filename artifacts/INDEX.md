# Artifacts Index

## 2026-03-27

- `artifacts/code-simplifier/`: targeted hill-climb harness/test cleanup run
- `artifacts/skill-edit/`: internal doctrine capture for fail-fast contracts, migration-only compatibility, and test seam guidance

## 2026-04-01

- `artifacts/hill_climb/`: no retained active research lane after stale-run cleanup; start a fresh run_id before resuming hill climbing
- `artifacts/hill_climb_smoke/apr01-audit-smoke/`: retained smoke-harness lane under the current protected-surface fingerprint

Per-run contract:

- keep only `run.json`, `results.jsonl`, `results.tsv`, `incumbents/`, and `snapshots/`
- do not recreate per-evaluation `evaluations/` trees
- normalize any legacy run with `amm-match hill-climb compact --artifact-root <root>`
- do not retain old probe, compare, or superseded baseline runs once the active lane is updated
