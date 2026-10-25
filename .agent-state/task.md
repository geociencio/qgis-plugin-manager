# Active Task: P1 Backlog

## Status
- **Phase**: P1 (6/6 complete)
- **Progress**: 100%
- **Status**: ✅ P1 complete (2026-10-25); P2/architecture backlog pending.

## Objectives
1. [x] Consolidate root `AGENTS.md` as the project source of truth; framework docs
   are referenced instead of duplicated, with a regression test.
2. [x] Use `.agent/scaffold/qgis/` as the only QGIS domain pack and remove the
   unused root `scaffold/qgis/` copy.
3. [x] Add end-to-end tests for deploy/package (real CLI, isolated filesystem).
4. [x] Harden CLI paths: symlinks, POSIX ZIP names and explicit `--trust` for
   hooks/dependencies.
5. [x] Add `py.typed` + strict mypy, remove dead `cli.py`/`get_ignore_func`, and
   fix README ignore syntax / Makefile/docs drift.
6. [x] Document `// turbo` as opencode-only and keep `qa-docker` as a non-adopted
   upstream alias; add guard tests.

## Todo
- [x] Pick the first P1 item with the user.
- [x] Write the technical plan before touching code.
- [x] Root AGENTS consolidation + `tests/test_agent_docs.py`.
- [x] Removed root `scaffold/qgis/`; framework pack is canonical.
- [x] Added 8 E2E tests in `tests/test_e2e_cli.py`; fixed purge with
  absolute `--profile`.
- [x] Symlink confinement, POSIX ZIP arcnames, unsafe version rejection and
  `--trust` gating for hooks/dependencies.
- [x] `py.typed`, strict mypy, Makefile/README/docs cleanup, dead `cli.py`
  and `get_ignore_func`.
- [x] Documented opencode-only `// turbo` and non-adopted `qa-docker` alias;
  244 tests, 90.45 % coverage.
- [ ] P1 complete; pick a P2/architecture item.

## Context
- Framework: **agentic-forge** `.agent/` submodule **v1.4.2** (`b264e35`), clean.
- Quality: **244 project tests**, **90.45 %** line coverage; **37 framework tests**;
  ruff/format/mypy clean; `forge.py validate` and `metrics validate` pass.
- Previous phase: P0 hardening + framework adoption, archived at
  `.agent-state/history/tasks/task_2026-10-19_p0_framework.md`.
- P1-1: root `AGENTS.md` is canonical; generic framework tables are linked from
  `.agent/AGENTS.md` / `.agent/QUICK_REFERENCE.md`; `tests/test_agent_docs.py`
  prevents drift.
- P1-2: QGIS domain pack is framework-only at `.agent/scaffold/qgis/`;
  `scaffold/mining/` remains project-owned; `tests/test_agent_docs.py` guards it.
- P1-3: `tests/test_e2e_cli.py` covers deploy/package via subprocess; found and
  fixed `--purge-backups` for absolute `--profile` paths.
- P1-4: symlink sources/targets are confined; ZIP members use `/`; unsafe
  versions are rejected; hooks/deps require explicit `--trust`.
- P1-5: package is typed (`py.typed`, `mypy --strict`), Makefile targets are
  current, README ignore syntax is fixed, and dead `cli.py` is gone.
- P1-6: `// turbo` documented as opencode-only; `qa-docker` remains a
  deprecated upstream alias and is not adopted by this project.
- Next: `.agent-state/next_steps.md` (P2 backlog).
