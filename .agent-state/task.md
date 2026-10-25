# Active Task: P2 Release & Architecture Cleanup

## Status
- **Phase**: P2 (2/2 complete)
- **Progress**: 100%
- **Status**: ✅ P2 complete and session closed (2026-10-25, `p1_p2_completion`);
  no active project backlog.

## Objectives
1. [x] Normalize release-note filenames to `vX.Y.Z.md`, archive the legacy v0.6.2
   duplicate and add a workflow fallback for old tags.
2. [x] Annotate the upstream Gen 7/8 architecture plans and record the project
   position without editing the shared `.agent` submodule.

## Todo
- [x] Normalize notes and update the release workflow.
- [x] Create `docs/architecture/AGENTIC_SYSTEM_PLANS.md` and link checks.
- [x] Refresh metrics and close P2.

## Context
- Framework: **agentic-forge** `.agent/` submodule **v1.4.2** (`b264e35`), clean.
- Quality: **248 project tests**, **90.45 %** line coverage; **37 framework tests**;
  ruff/format/strict mypy clean; `forge.py validate` and `metrics validate` pass.
- Previous phase: P1 complete, archived at
  `.agent-state/history/tasks/task_2026-10-25_p1_complete.md`.
- Release notes: active files use `vX.Y.Z.md`; workflow also accepts
  `RELEASE_NOTES_vX.Y.Z.md` and falls back to a generic body.
- Architecture: Gen 7 is superseded by Gen 8; Gen 8 remains upstream-owned and
  Agentic Forge v1.4.2 is the baseline.
