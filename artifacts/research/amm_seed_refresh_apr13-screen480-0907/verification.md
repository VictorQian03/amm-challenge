# Verification

- Verified the fresh retained lane exists: `apr13-screen480-0907`.
- Verified the new lane is seeded from the current incumbent at `473.616393`.
- Verified the breakout gate is recorded at `screen >= 480`.
- Verified the prior lane read surfaces still identify calm-slice weakness and spiky fee motion as the dominant bottlenecks.
- Verified `screen_0002` failed directionally even though it reduced `max_fee_jump`, which rules out broad fee-surface cheapening as a viable first move.
- Verified `screen_0003` improved `arb_edge`, `arb_loss_to_retail_gain`, `low_decile_mean_edge`, `low_retail_mean_edge`, and `max_fee_jump`, but only by `+0.564841` overall.
