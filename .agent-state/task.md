# Active Task: P0 Remediation (0.10.1)

## Status
- **Phase**: P0 (5/5 fixes complete)
- **Progress**: 100%
- **Status**: ✅ P0 implemented and 0.10.1 prepared locally (2026-10-25);
  push/tag/publication pending.

## Fixes
1. [x] Collision-safe deploy backups (microseconds + suffix).
2. [x] Repeatable `compile --type`.
3. [x] `package --release-version` consistency validation.
4. [x] `deploy --yes` for non-interactive purge/create/deploy.
5. [x] `clean --dry-run` and `--keep-generated` protection.

## Coverage
- [x] Risk-weighted test coverage: 331 tests, 96.55 % statements,
  91.47 % branches, gates raised to 95/90.
- [x] E2E contracts for the P0 fixes.

## Next
- Review/publish 0.10.1.
- P1: repo-check pruning, deploy manifest, reflink backups, compiled-output
  freshness.
- P2: JSON, ignore explain, max-cc, dry-run, profiles, require-docs, shell=False.

## Context
- Framework: **agentic-forge** `.agent/` submodule **v1.4.2** (`b264e35`), clean.
- Quality: **279 project tests**, **90.80 %** combined coverage; branch gate 90 %;
  **37 framework tests**; ruff/format/strict mypy clean; C901 = 0.
- Previous phase: P3 complete, archived at
  `.agent-state/history/tasks/task_2026-10-25_p3_platform.md`.
