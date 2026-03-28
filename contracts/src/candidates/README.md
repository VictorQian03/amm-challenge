# Candidate Workspace

This directory is the candidate library for hill-climb submissions.

Start by copying a candidate into `../Strategy.sol` and editing only the strategy logic you want to test there. Keep the contract name `Strategy` so the existing compiler and harness can load it without special cases.
Keep imports rooted at `./AMMStrategyBase.sol` and `./IAMMStrategy.sol`; the harness compiles source text directly, so candidate files should not rely on their subdirectory location for import resolution.
