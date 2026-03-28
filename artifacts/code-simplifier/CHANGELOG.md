# Code Simplifier Changelog

## 2026-03-27-hill-climb-contract-cleanup

- tightened the hill-climb harness to reject missing continuity files and malformed retained manifests instead of reconstructing or swallowing them
- enforced `contracts/src/Strategy.sol` as the documented active hill-climb eval path in the CLI
- added regression coverage for malformed legacy manifests and CLI path rejection while keeping hill-climb tests on explicit fake collaborators
