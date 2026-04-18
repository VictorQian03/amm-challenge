# Artifacts Index

Start here:

- `artifacts/index.json`: machine-readable cross-run catalog for agents
- `docs/agent_harness_guide.md`: canonical read order for retained runs, historical evals, research memos, and idea-generation inputs
- this file: human narrative for what changed across dates

Current state:

- active retained `screen` lane: none; seed a fresh `run_id` before the next mutation
- latest historical read surface on the current protected-surface fingerprint: `apr18-screen480-1132`
- stale `apr16-screen480-1758` retained-lane artifacts were pruned after the run was abandoned

## 2026-03-27

- `artifacts/code-simplifier/`: targeted hill-climb harness/test cleanup run
- `artifacts/skill-edit/`: internal doctrine capture for fail-fast contracts, migration-only compatibility, and test seam guidance

## 2026-04-01

- `artifacts/hill_climb_smoke/apr01-audit-smoke/`: retained smoke-harness lane under the current protected-surface fingerprint
- `docs/plans/completed/apr01-screen420-2134.md`: retained narrative for the pruned `apr01` research round after the separate research directory was folded back into plan history

## 2026-04-10

- `artifacts/research/amm_dynamic_fee_apr10-screen480-0931/`: source-backed worker map and outcome log for the `480`-targeted round

## 2026-04-11

- `artifacts/hill_climb/apr11-screen480-0948/`: sole retained `screen` lane after artifact hygiene cleanup; baseline `473.616393`, best raw replay `473.668925`, breakout gate still pending at `480.0`
- under the current checkout it is read-only because protected-surface drift now requires a fresh `run_id` before any further mutation/resume
- transient `apr11-screen480-0948-w0*` worker lanes and superseded retained run `apr10-screen480-0947/` were pruned after their findings were folded into the retained lane and plan docs

## 2026-04-12

- `artifacts/hill_climb/apr12-screen480-1130/`: retained historical `screen` lane on the prior protected-surface fingerprint; baseline `473.616393`, breakout gate stayed pending at `480.0`, and the next structural retry was deferred
- `artifacts/research/amm_branch_portfolio_apr12-screen480-1130/`: branch portfolio memo and source log for the five-hypothesis batch that seeded that historical lane
- `artifacts/hill_climb/apr11-screen480-0948/` remains read-only history and should not be resumed for mutation on this checkout

## 2026-04-13

- `artifacts/hill_climb/apr13-screen480-0907/`: latest retained historical `screen` lane on the current protected-surface fingerprint; baseline `473.616393`, breakout gate remained pending at `480.0`, `screen_0005` is the best raw survivor, and the batch closed with no queued next hypothesis
- `artifacts/research/amm_seed_refresh_apr13-screen480-0907/`: research memo, new-source log, and hypothesis tracker for that historical lane
- `artifacts/hill_climb/apr12-screen480-1130/` and `artifacts/hill_climb/apr13-screen480-0907/` are read-only history for planning; the next mutation should use a fresh `run_id`

## 2026-04-17

- `artifacts/hill_climb/apr17-screen480-0834/`: retained historical `screen` lane on the current protected-surface fingerprint; baseline `473.616393`, strongest raw branch `screen_0004 @ 483.890738`, and the batch closed with no queued next hypothesis after the family was exhausted
- `docs/plans/completed/apr17-screen480-0834.md`: retained narrative for the closed `apr17-screen480-0834` batch after its successor lane became active
- `artifacts/hill_climb/apr17-screen480-0928/`: retained historical `screen` lane; baseline `473.616393`, strongest raw branch `screen_0009 @ 485.703883`, and the lane is closed after the stop-rule threshold was hit
- `docs/plans/completed/apr17-screen480-0928.md`: canonical retained narrative for the closed `apr17-screen480-0928` lane, with the old active-path stub preserved only as a redirect target for historical metadata

## 2026-04-18

- `artifacts/hill_climb/apr18-screen480-1132/`: latest retained historical `screen` lane on the current protected-surface fingerprint; official incumbent stayed at `473.616393`, best raw branch reached `screen_0008 @ 485.923771`, and the harness stopped the lane after 8 consecutive non-improving screen evals
- `docs/plans/completed/apr18-screen480-1132.md`: canonical retained narrative for the closed `apr18-screen480-1132` lane, with the old active-path stub preserved only as a redirect target for historical metadata

Per-run contract:

- keep only `run.json`, `state.json`, `results.jsonl`, `results.tsv`, `history.jsonl`, `hypotheses/`, `incumbents/`, `snapshots/`, and derived `notebook/` surfaces
- keep the machine-readable cross-run catalog at `artifacts/index.json`
- do not recreate per-evaluation `evaluations/` trees
- do not retain old probe, compare, quarantine, or superseded baseline runs once the active lane is updated
