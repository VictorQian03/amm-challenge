# Strategy Framework

The active research architecture is now the hill-climb harness.

Primary references:

1. [Hill-Climb Harness](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/plans/active/hill_climb_harness.md)
2. [Program Loop](/Users/victorqian/Desktop/opt_arena/simple_amm/program.md)
3. [Canonical Loop Contract](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/hill_climb_loop.md)

Core contract:

- optimize `mean_edge`
- keep the competition evaluator fixed
- iterate on one candidate source file at a time
- vary only `n_simulations` by stage
- do not use paired local champion evals
- retain at most one active artifact lane under `artifacts/hill_climb/<run_id>/` plus one current smoke lane under `artifacts/hill_climb_smoke/<run_id>/`
- if no artifact lane is active, the next action is to seed a fresh run rather than resume history
