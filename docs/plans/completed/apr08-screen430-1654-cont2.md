# Hill-Climb Continuation: apr08-screen430-1654-cont2

## Objective

- Continue retained run `apr08-screen430-1654` from the new incumbent `screen_0006 @ 457.851560`.
- Follow harness guidance through refinement, then pivot, and stop when the run hits the retained stop rule.

## Start State

- Incumbent at continuation start: `screen_0006 @ 457.851560`
- Workspace restored to incumbent source before each new branch.
- Harness guidance at start: `continue (refine in 1, pivot in 3, stop in 6)`

## Main Lane Results

| eval | hypothesis | result |
| --- | --- | --- |
| `screen_0009` | `h004-event-threshold-plus-quiet` | `457.852256 discard` |
| `screen_0010` | `h005-hazard-weighted-event` | `454.520743 discard` |
| `screen_0011` | `h003-threshold-event-surcharge` | `458.648102 discard` |
| `screen_0012` | `h006-fixed-ultraquiet-rebate` | `457.685721 discard` |
| `screen_0013` | `h007-directional-burst-shift` | `460.594212 discard` |
| `screen_0014` | `h007-directional-burst-shift` | `461.223655 discard` |

## Worker Evidence

- `w08` suggested replacing the broad linear calm rebate with a fixed ultra-quiet rebate. Adapted to the incumbent, that became `screen_0012`, which regressed relative to `screen_0006`.
- `w09` hazard-dominant event weighting regressed sharply and did not become a retained candidate.
- `w10` found a cleaner local refine: increase only the above-threshold burst slope from `1500` to `1700 bps`. Adapted to the incumbent, that became `screen_0011`, which improved raw edge by `0.796542` but still missed the promotion margin badly.

## Decision Log

- First refine after the new incumbent: add a tiny thresholded extra quiet rebate on top of the incumbent. That produced `screen_0009`, effectively flat versus the incumbent and not operationally meaningful.
- Next adjacent refine: hazard-weight the event threshold signal. That became `screen_0010` and clearly regressed.
- Last refine before pivot: keep the incumbent and raise only the post-threshold burst slope to `1700 bps`. That became `screen_0011`, the best raw result within the original event-threshold family, but still far short of promotion.
- Harness guidance then switched to `pivot now`, so the search moved away from broad shared event carry and into new families.
- Pivot 1: replace the broad linear calm rebate with a fixed ultra-quiet rebate. Adapted retained eval `screen_0012` regressed.
- Pivot 2: move part of the above-threshold burst charge from the shared spread into the toxic side only. `screen_0013` improved raw edge by `2.742652`; the stronger directional split in `screen_0014` improved raw edge further to `+3.372096`, but neither came close to the `~19.29` promotion margin.
- After `screen_0014`, the retained run hit `8` consecutive non-improving screen evaluations and the harness guidance became `stop now`.

## Final State

- Retained incumbent remains `screen_0006 @ 457.851560`
- Best raw non-promoted continuation source: `screen_0014 @ 461.223655`
- Workspace restored to the retained incumbent after stop guidance fired
- Current retained guidance: `stop now (8 consecutive non-improving screen evaluations; threshold 8)`

## Notes

- The event-threshold family was clearly the right macro pivot for this run and remains the source of the current incumbent.
- Once `screen_0006` was established, the best remaining local gains came from making burst pricing more directional rather than cheaper.
- Even the best post-incumbent raw variant, `screen_0014`, was still only `+3.372096` over the incumbent, far below the uncertainty-aware promotion margin, so continued local tuning on this line is not justified under the harness contract.
