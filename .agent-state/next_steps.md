# Next Steps

**Date**: 2026-10-25
**Last session**: `p0_and_forge_v1_4_2` (closed; CLI P0 + Agentic Forge v1.4.2)
**Current session**: P1 and P2 complete (2026-10-25); no active project backlog.
**Context**: P1 closed docs/domain-pack/E2E/path/trust/typing work; P2 normalized release
notes and annotated the upstream architecture plans. Project: **248 tests**, **90.45 %**
line coverage; framework v1.4.2 with 37 tests.

**Completed (this cycle):**
- [x] Adopted Agentic Forge **v1.4.1** (upstream P0).
- [x] Adopted **v1.4.2** (TOML mypy + metrics/cache scan fixes); framework CI
      passes without workarounds.
- [x] `.agent-state/memory/agent_metrics.json` + `scripts/sync_metrics.py`
- [x] `memory_policy.md`, `AI_CONTEXT.md`, refreshed task/next_steps/lessons
- [x] `memory prune` dry-run by default; `--apply` for mutations
- [x] Validator covers scaffolds, links, canonical agent IDs, state, trigger conflicts
- [x] `.agent/tools` split and cleaned (ruff/format/mypy/C90/module size)
- [x] `.agent/tests` (37 tests) and CI steps for lint/type/test/validate/metrics
- [x] Workflows adapted to real repo commands (start/close/tests/release)
- [x] Sibling compatibility: overlay workflows, custom agents from `opencode.json`,
      project commands in `forge.toml`, domain-pack metrics skipped, strict mode opt-in
- [x] P1-1: consolidated root `AGENTS.md`; framework docs linked, no duplicate tables;
      `tests/test_agent_docs.py` guards the links.
- [x] P1-2: `.agent/scaffold/qgis/` is the only QGIS pack; removed the unused root
      `scaffold/qgis/` copy.
- [x] P1-3: 8 end-to-end deploy/package tests in `tests/test_e2e_cli.py`; fixed
      `--purge-backups` with absolute `--profile`.
- [x] P1-4: symlink confinement, POSIX ZIP arcnames, unsafe-version rejection
      and explicit `--trust` for hooks/dependencies.
- [x] P1-5: `py.typed`, strict mypy, Makefile/README/docs cleanup and dead
      `cli.py` removal.
- [x] P1-6: `// turbo` documented as opencode-only; `qa-docker` is a
      non-adopted upstream alias.
- [x] P2-1: release notes normalized to `vX.Y.Z.md`; workflow fallback added.
- [x] P2-2: Gen 7/8 plans annotated in `docs/architecture/AGENTIC_SYSTEM_PLANS.md`.
      Project tests: 248, coverage 90.45 %.

**Pending:**
- No active project items. Remaining framework work belongs upstream in `agentic-forge`.

**Command to resume:**
`/start-session` (it now refreshes metrics and runs the validators).
