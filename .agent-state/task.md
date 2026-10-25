# Active Task: P1 Backlog

## Status
- **Phase**: P1 (2/6 complete)
- **Progress**: 33%
- **Status**: ✅ P1-2 QGIS domain-pack deduplication complete (2026-10-25); next item pending.

## Objectives
1. [x] Consolidate root `AGENTS.md` as the project source of truth; framework docs
   are referenced instead of duplicated, with a regression test.
2. [x] Use `.agent/scaffold/qgis/` as the only QGIS domain pack and remove the
   unused root `scaffold/qgis/` copy.
3. [ ] Add end-to-end tests for deploy/package.
4. [ ] Harden CLI P1 paths: symlink traversal, Windows ZIP separators and the
   hooks/dependency trust model.
5. [ ] Add `py.typed` + strict mypy, remove dead `cli.py`, and fix README ignore
   syntax / docs-Makefile drift.
6. [ ] Decide on `// turbo` hints and the deprecated `qa-docker` alias.

## Todo
- [x] Pick the first P1 item with the user.
- [x] Write the technical plan before touching code.
- [x] Root AGENTS consolidation + `tests/test_agent_docs.py`.
- [x] Removed root `scaffold/qgis/`; framework pack is canonical.
- [ ] Pick the next P1 item with the user.

## Context
- Framework: **agentic-forge** `.agent/` submodule **v1.4.2** (`b264e35`), clean.
- Quality: **221 project tests**, **90.48 %** line coverage; **37 framework tests**;
  ruff/format/mypy clean; `forge.py validate` and `metrics validate` pass.
- Previous phase: P0 hardening + framework adoption, archived at
  `.agent-state/history/tasks/task_2026-10-19_p0_framework.md`.
- P1-1: root `AGENTS.md` is canonical; generic framework tables are linked from
  `.agent/AGENTS.md` / `.agent/QUICK_REFERENCE.md`; `tests/test_agent_docs.py`
  prevents drift.
- P1-2: QGIS domain pack is framework-only at `.agent/scaffold/qgis/`;
  `scaffold/mining/` remains project-owned; `tests/test_agent_docs.py` guards it.
- Next: `.agent-state/next_steps.md` (P1/P2 backlog).
