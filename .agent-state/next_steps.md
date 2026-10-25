# Next Steps

**Date**: 2026-10-25
**Last session**: `p0_and_forge_v1_4_2` (closed; CLI P0 + Agentic Forge v1.4.2)
**Current session**: started 2026-10-25; P1 item not selected yet.
**Context**: Agent Framework P0 is complete: metrics bootstrap, safe pruning, extended
validator, CI gate, workflow adaptation and tooling dogfooding. The repository also has
the earlier CLI P0 hardening (220 tests, 90.48 % line coverage).

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
      `scaffold/qgis/` copy. Project tests: 221.

**Pending (P1/P2):**
- [ ] Remove the remaining `// turbo` runtime hints or document them as opencode-only.
- [ ] Decide whether the `qa-docker` skill should remain active (the repository has no
      Docker setup; workflows now use local commands).
- [ ] Add end-to-end tests for deploy/package (CLI P1 backlog).
- [ ] Address CLI P1 items: symlink traversal, Windows ZIP separators, trust model for
      hooks/dependencies, `py.typed`/strict mypy, dead `cli.py`, README ignore syntax,
      docs/Makefile drift, release-note filenames.
- [ ] Archive/annotate the Gen 7/8 architecture plans.

**Command to resume:**
`/start-session` (it now refreshes metrics and runs the validators).
