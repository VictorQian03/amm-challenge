# PRD

## Problem

The current AMM strategy is locally competitive but repeatedly fails to improve enough on the canonical `screen` block because calm relief is too broad and fee motion is too spiky.

## Decision Target

Produce a new five-branch hill-climb batch for a fresh retained run and execute the highest-priority branch first.

## Acceptance Criteria

- Fresh retained lane exists with a seeded baseline and `screen >= 480` breakout gate.
- Five materially different hypotheses are documented and registered.
- The first branch is implemented and evaluated on the new lane.

## Non-goals

- Retuning the old run in place.
- Repeating broad calm-rebate, shock-spike, retail-share, or cheap-router-first branches.
