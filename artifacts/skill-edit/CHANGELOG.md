# Skill Edit Changelog

## 2026-03-27-internal-doctrine-antipattern-capture

- added a concise engineering-quality invariant against preserving compatibility shims, inferred-state recovery, and monkeypatch-only test seams when explicit contracts are available
- added deep-reference clean-code guidance restricting compatibility behavior to explicit migration paths and preferring fakeable collaborators over brittle monkeypatching
- added iterative-loop doctrine requiring fail-fast handling for missing continuity state and malformed or ambiguous retained artifacts
