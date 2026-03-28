# Skill Edit Review

- Run ID: `2026-03-27-internal-doctrine-antipattern-capture`
- Repo root: `/Users/victorqian/Desktop/opt_arena/simple_amm`

## Scope

- Reviewed and updated:
  - `/Users/victorqian/.codex/skills/domain/domain_engineering_quality.md`
  - `/Users/victorqian/.codex/skills/domain/references/engineering_quality/clean_code.md`
  - `/Users/victorqian/.codex/skills/domain/references/agent_orchestration/iterative_optimization_harness.md`

## Capture Summary

- Captured the anti-pattern that strict runtime contracts should not preserve compatibility shims or inferred-state recovery once an explicit contract exists.
- Captured the anti-pattern that monkeypatch-heavy tests over private internals are a smell when explicit constructor seams or fakeable collaborators can replace them.
- Captured the loop-specific rule that eval/resume/status flows must not reconstruct required continuity state from ledgers, legacy folders, or naming heuristics.
- Kept progressive disclosure intact by adding one concise quick-load invariant and pushing the detailed guidance into the canonical deep references.

## Prompt/Schema Stability

- No tool schema or prompt prefix contracts were changed.
- The update was limited to domain guidance and deep-reference doctrine.

## Verification

- Verified the inserted guidance in the three target files by reading the updated line ranges after patching.
- No code tests were required because this change only updated internal markdown doctrine.
