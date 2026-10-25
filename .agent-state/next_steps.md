# Next Steps

**Date**: 2026-10-25
**Last session**: `p0_and_forge_v1_4_2` (closed; CLI P0 + Agentic Forge v1.4.2)
**Current session**: P1 complete (2026-10-25); P2/architecture backlog pending.
**Context**: P1 is complete: docs consolidated, QGIS pack unified, deploy/package E2E,
path/trust hardening, strict typing and framework-hint decisions. Project: **244 tests**,
**90.45 %** line coverage; framework v1.4.2 with 37 tests.

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
      non-adopted upstream alias. Project tests: 244, coverage 90.45 %.

**Pending (P2):**
- [ ] Normalize release-note filenames (`vX.Y.Z.md` vs `RELEASE_NOTES_v*.md`) and add a
      fallback in the release workflow.
- [ ] Archive/annotate the Gen 7/8 architecture plans.

**Command to resume:**
`/start-session` (it now refreshes metrics and runs the validators).
