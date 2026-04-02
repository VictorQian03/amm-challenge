# Artifacts Index

## 2026-03-27

- `artifacts/code-simplifier/`: targeted hill-climb harness/test cleanup run
- `artifacts/skill-edit/`: internal doctrine capture for fail-fast contracts, migration-only compatibility, and test seam guidance

## 2026-04-01

- `artifacts/hill_climb/apr01-screen420-2134/`: retained coordinated hill-climb lane carrying the `LatentStateIncumbentGapAwareV4` winner through `screen`, `climb`, `confirm`, and `final`
- `artifacts/hill_climb_smoke/apr01-audit-smoke/`: retained smoke-harness lane under the current protected-surface fingerprint
- `artifacts/research/amm_dynamic_fee_apr01-screen420-2134/`: external AMM dynamic-fee evidence memo and hypothesis ranking linked to retained run `apr01-screen420-2134`

Per-run contract:

- keep only `run.json`, `results.jsonl`, `results.tsv`, `incumbents/`, and `snapshots/`
- do not recreate per-evaluation `evaluations/` trees
- normalize any legacy run with `amm-match hill-climb compact --artifact-root <root>`
- do not retain old probe, compare, or superseded baseline runs once the active lane is updated
