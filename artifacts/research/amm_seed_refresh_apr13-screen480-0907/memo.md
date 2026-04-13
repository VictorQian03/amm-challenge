# Research Memo: apr13-screen480-0907

## Question

What fresh hypothesis batch should seed the new retained `screen` run, given that the prior lane repeatedly failed from over-spiky fee motion, calm-slice weakness, and a router that underpriced too broadly?

## Findings

1. The current bottleneck is still calm / low-retail / weak-decile performance, not high-retail or high-volatility performance.
2. The dominant mechanical failure is not merely "fees too high" or "fees too low"; it is noisy and overly abrupt fee motion that either stays cheap too long or flattens protection.
3. Previously unread AMM sources strengthen two design ideas that were not yet tried cleanly in this repo:
   - filtered volatility-sensitive fee floors
   - explicit decomposition between symmetric baseline spread and asymmetric adverse-selection protection
4. Production AMM docs suggest a practical policy template that fits this one-file harness: volatility-driven dynamic fees plus exponential or scheduled decay back toward a floor.
5. The next batch should keep one truly fresh structural retry, but the first implementation should stay closer to the incumbent spine and attack the fee-motion bottleneck directly.

## Recommended First Branch

`fee-discipline-vol-accumulator-floor`

- Use a filtered reference spot and a decayed volatility accumulator instead of relying only on instantaneous event repricing.
- Map that accumulator into a protective fee floor with a convex transform, so meaningful clusters widen the floor while small alternating noise does not.
- Release the floor with exponential decay after calm gaps rather than hard final-output slew caps.
- Keep the incumbent side-specific risk and opportunity cuts, but bound calm relief more tightly.

## Source Notes

- The structural AMM model argues fixed fees are inefficient and optimal fees should react to volatility, which supports replacing part of the current event spike logic with a filtered volatility floor.
- The Myersonian AMM paper argues the effective spread decomposes into adverse-selection and monopoly components, which supports keeping a symmetric floor and separate side-specific toxicity adjustments.
- Meteora DAMM docs and code references show a practical combination of dynamic fee logic and exponential fee scheduling, which is a useful control template for smoothing release without letting the book stay cheap continuously.

## Confidence

- High confidence that the next seed should focus on smoother protective floors and capped calm relief.
- Medium confidence that a volatility accumulator beats the incumbent event carry on this evaluator; it is still an untested branch in this repo.
- Medium confidence that a second-generation structural router is worth keeping in the batch, but not as the first spend.
