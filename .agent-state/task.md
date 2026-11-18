# Phase: 0.17.0 Refactor

## Status
- **Phase**: B1 complete (2026-11-18); B2 next.
- **Refactor**: `PathPolicy`/`ProjectWalker` centralized; compile, package,
  clean, repository and discovery migrated.
- **Quality**: 441 tests, 96.24 % statements, 90.46 % branches, 94.85 % combined,
  C901 = 0; runtime dependencies = 0.

## Completed
1. [x] B1 — PathPolicy and ProjectWalker.
2. [ ] B2 — DeployWorkflow.
3. [ ] B3 — PackageWorkflow.
4. [ ] B4 — console rename.
5. [ ] B5 — typed error boundary.
6. [ ] B6 — atomic TOML updates.
7. [ ] B7 — external input validation.
8. [ ] B8 — release 0.17.0.

## Next
- B2: extract `DeployWorkflow` from `DeployCommand`.
- Resume with `/start-session`.
