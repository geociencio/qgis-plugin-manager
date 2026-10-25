# Active Task: P3 Platform Controls

## Status
- **Phase**: P3 (7/7 implemented)
- **Progress**: 100%
- **Status**: ✅ P3 core implemented (2026-10-25); compatibility deviations recorded.

## Objectives
1. [x] Nested `.qgisignore`/`.gitignore` rules with ordered negation.
2. [x] Hook policy with timeout, allowlisted environment and non-shell option.
3. [x] Bounded dependency installation with timeout and dry-run.
4. [x] `compile --jobs` with ordered callbacks.
5. [x] External `qgis_manager.commands` entry points.
6. [x] Init/bump contract E2E tests.
7. [x] Docs/help/changelog refreshed.

## Deviations from plan
- Hook shell mode defaults to `True` for backward compatibility; `HookPolicy(shell=False)`
  is available via the API but not the default.
- `compile_jobs` is exposed as `compile --jobs`, not yet read from `project.toml`.
- Dependency index/constraints options are not added; timeout + dry-run are.
- Nesting is covered; `.git/info/exclude` remains unsupported.

## Context
- Framework: **agentic-forge** `.agent/` submodule **v1.4.2** (`b264e35`), clean.
- Quality: **269 project tests**, **91.03 %** combined coverage; branch gate 90 %;
  **37 framework tests**; ruff/format/strict mypy clean; C901 = 0.
- Previous phase: P2 complete, archived at
  `.agent-state/history/tasks/task_2026-10-25_p2_quality.md`.
