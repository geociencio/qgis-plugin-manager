# Next Steps

**Date**: 2026-10-19
**Context**: Agent Framework P0 is complete: metrics bootstrap, safe pruning, extended
validator, CI gate, workflow adaptation and tooling dogfooding. The repository also has
the earlier CLI P0 hardening (217 tests, 90.48 % line coverage).

**Completed (this cycle):**
- [x] Adopted Agentic Forge **v1.4.1** (upstream P0).
- [ ] Upstream v1.4.2: fix `forge_paths` TOML decode mypy false positive and
      `should_skip_file` self/cache scan; remove the CI `misc` workaround after.
- [x] `.agent-state/memory/agent_metrics.json` + `scripts/sync_metrics.py`
- [x] `memory_policy.md`, `AI_CONTEXT.md`, refreshed task/next_steps/lessons
- [x] `memory prune` dry-run by default; `--apply` for mutations
- [x] Validator covers scaffolds, links, canonical agent IDs, state, trigger conflicts
- [x] `.agent/tools` split and cleaned (ruff/format/mypy/C90/module size)
- [x] `.agent/tests` (33 tests) and CI steps for lint/type/test/validate/metrics
- [x] Workflows adapted to real repo commands (start/close/tests/release)
- [x] Sibling compatibility: overlay workflows, custom agents from `opencode.json`,
      project commands in `forge.toml`, domain-pack metrics skipped, strict mode opt-in

**Pending (P1/P2):**
- [ ] Consolidate root `AGENTS.md`, `.agent/AGENTS.md` and `QUICK_REFERENCE.md` into one
      source of truth (Gen 8 item still open).
- [ ] Choose one QGIS domain pack and remove the divergent copy (`scaffold/qgis` vs
      `.agent/scaffold/qgis`).
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
