# Hill-Climb Continuation: apr08-screen430-1654-cont1

## Objective

- Continue retained run `apr08-screen430-1654`.
- Improve `mean_edge` for `contracts/src/Strategy.sol` at `screen`.
- Keep the retained incumbent as the restore point unless a candidate clearly beats it.

## Baseline At Continuation Start

- Incumbent at continuation start: `screen_0001 @ 434.301202`
- Live source hash at continuation start: `8af1aa3d1ecb65a442be50cf347044f2be9212eb9bde2e28a757846580bb1de4`
- Existing breakout gate remained passed: `screen >= 430`

## Research Direction

- Prior quiet-divergence and calm-step families had saturated near the incumbent.
- External references pointed toward a threshold-style fee schedule: stable, competitive fees in normal conditions and sharply higher protection only in stressed regimes.
- Search therefore focused on threshold-style calm/event overlays rather than another broad state-family rewrite.

## Worker Families

| worker | run_id | hypothesis | status |
| --- | --- | --- | --- |
| w05 | `apr08-screen430-1654-w05-threshold-regime-rebate` | Hard threshold rebate on shared carry in very quiet regimes. | completed, best `434.640053` |
| w06 | `apr08-screen430-1654-w06-threshold-event-surcharge` | Lower normal-condition observation carry and add a steep surcharge only above a shock threshold. | completed, worker best recorded `440.755136`; the patched follow-on variant became retained `screen_0006` |
| w07 | `apr08-screen430-1654-w07-calm-base-step` | Tiny calm-only base-fee step-down after longer gaps. | completed, all evaluated variants neutral at `434.301202` |

## Main Lane Results

| eval | hypothesis | result |
| --- | --- | --- |
| `screen_0005` | `h002-threshold-calm-step` | `434.268314 discard` |
| `screen_0006` | `h003-threshold-event-surcharge` | `457.851560 keep` |
| `screen_0007` | `h003-threshold-event-surcharge` | `457.842624 discard` |
| `screen_0008` | `h003-threshold-event-surcharge` | `457.837299 discard` |

## Winning Change

- Replaced the linear observation carry
  - from `volObservation * 650 bps + hazardObservation * 1100 bps`
- with a thresholded event surcharge
  - `eventSignal = min(WAD, volObservation + hazardObservation)`
  - `eventCarry = eventSignal * 300 bps`
  - extra `+ (eventSignal - 8 bps) * 1500 bps` only above the 8 bps shock threshold
- Kept the latent-state engine, quiet recentering, and calm rebate structure unchanged.

## Decision Log

- `2026-04-08`: continued retained run `apr08-screen430-1654` from incumbent `screen_0001 @ 434.301202`.
- `2026-04-08`: tested a local threshold calm-step family first; it regressed to `434.268314`, confirming that direct calm undercutting still leaked value in the weakest low-vol/low-retail slices.
- `2026-04-08`: worker `w05` found that a hard threshold rebate on shared carry could improve raw edge to `434.640053`, validating the threshold-fee direction but still leaving most of the opportunity untapped.
- `2026-04-08`: worker `w06` surfaced the stronger idea: threshold the event surcharge instead of the calm rebate path.
- `2026-04-08`: retained eval `screen_0006` promoted that family to the new incumbent at `457.851560`, clearing the promotion margin by `23.550358` versus a required `18.363203`.
- `2026-04-08`: two local refinements (`screen_0007`, `screen_0008`) both stayed within `0.015` of the new incumbent but did not beat it, so the run was parked back on `screen_0006`.

## Final State

- Current retained incumbent: `screen_0006 @ 457.851560`
- Current workspace source hash: `c158f16ec38db0043ae8ce215bec6075a545a6fd15da6a57353b528684619cd6`
- Current stop guidance: `continue (refine in 1, pivot in 3, stop in 6)`

## Notes

- The big gain came from charging materially more only when the combined short-lived event signal is genuinely large, while leaving moderate states cheaper than the old linear observation carry.
- The two follow-up variants suggest the current winner sits near a local optimum for this family: softening moderate-state pricing even slightly reduced `mean_edge`.
