# Strategy Framework

The active research architecture is now the hill-climb harness.

Primary references:

1. [Hill-Climb Harness](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/plans/active/hill_climb_harness.md)
2. [Program Loop](/Users/victorqian/Desktop/opt_arena/simple_amm/program.md)
3. [Iterative Loop Review And PRD](/Users/victorqian/Desktop/opt_arena/simple_amm/docs/plans/active/iterative_loop_review_and_prd.md)

Core contract:

- optimize `mean_edge`
- keep the competition evaluator fixed
- iterate on one candidate source file at a time
- vary only `n_simulations` by stage
- do not use paired local champion evals
- retain one active artifact lane at `artifacts/hill_climb/mar26-loop/` plus smoke sanity under `artifacts/hill_climb_smoke/smokecheck/`
