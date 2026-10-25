# Active Task: P0 Code Optimization

## Status
- **Phase**: P0 (6/6 complete)
- **Progress**: 100%
- **Status**: ✅ P0 optimization batch implemented (2026-10-25); see
  `docs/plans/p0_optimization_plan.md`.

## Objectives
1. [x] Instantiate CLI commands once (`fix(cli)`).
2. [x] Centralize command error handling in `BaseCommand.run`.
3. [x] Extract deploy orchestration helpers.
4. [x] Extract package orchestration helpers.
5. [x] Bound compile subprocesses and skip dev/vendor directories.
6. [x] Remove the dead `get_optional_fields` helper.

## Todo
- [x] Implement the six P0 commits.
- [x] Run project/framework/typing/coverage gates.
- [x] Update metrics and the optimization report/plan status.
- [ ] P1 refactors (validation split, metadata consolidation, compile context).

## Context
- Framework: **agentic-forge** `.agent/` submodule **v1.4.2** (`b264e35`), clean.
- Quality: **250 project tests**, **91.83 %** line coverage; **37 framework tests**;
  ruff/format/strict mypy clean.
- Remaining C901: `validate_metadata` (23), `validate_official_compliance` (11) and
  `load_ignore_patterns` (11); deferred to P1 per the plan.
- Previous phase: P2 complete, archived at
  `.agent-state/history/tasks/task_2026-10-25_p2_complete.md`.
