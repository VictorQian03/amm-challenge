# Artifacts Index

## 2026-03-26

- `artifacts/hill_climb/mar26-loop/`: retained active hill-climb lane
- `artifacts/hill_climb_smoke/smokecheck/`: retained smoke-harness lane

## 2026-03-27

- `artifacts/code-simplifier/`: targeted hill-climb harness/test cleanup run
- `artifacts/skill-edit/`: internal doctrine capture for fail-fast contracts, migration-only compatibility, and test seam guidance

Per-run contract:

- keep only `run.json`, `results.jsonl`, `results.tsv`, `incumbents/`, and `snapshots/`
- do not recreate per-evaluation `evaluations/` trees
- normalize any legacy run with `amm-match hill-climb compact --artifact-root <root>`
- do not retain old probe, compare, or superseded baseline runs once the active lane is updated
