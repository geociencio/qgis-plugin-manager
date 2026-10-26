# Next Steps

**Date**: 2026-10-25
**Last session**: `p0_p2_platform_release` (closed; 0.10.1, 0.11.0, 0.12.0 published)
**Current session**: portal security implemented (2026-10-25); 0.15.0 not prepared.
**Context**: portal security is implemented. Project: **405 tests**, **94.65 %**
combined coverage; framework v1.4.2.

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
- [x] P0-1..P0-6: CLI single instantiation/error wrapper, deploy/package
      extraction, compile timeouts/ignore scan and dead-helper removal.
- [x] P1-1..P1-6: ignore/validation/metadata splits, command registry,
      CompileContext and deploy content comparison.
- [x] P2-1..P2-7: narrowed exceptions, 90 % branch gate, portable config,
      ignore negation, Git-boundary root, BaseCommand.project_root and split
      test suites.
- [x] P3-1..P3-7: nested ignore rules, hook/dependency policies, compile jobs,
      entry-point commands and init/bump contracts.
- [x] P0-1..P0-5: collision-safe backups, repeatable --type, release-version
      validation, deploy --yes and clean dry-run.
- [x] Coverage initiative: 331 tests, 96.55 % statements, 91.47 % branches,
      95/90 gates and E2E P0 contracts.
- [x] P1-1..P1-4: pruned repo scan, deploy manifest, reflink backups and
      compile freshness (see the 0.11.0 release notes for its baseline).
- [x] P2-1..P2-7: JSON, ignore explain, max-cc, deploy dry-run, profiles,
      require-docs and non-shell hooks (baseline in the 0.12.0 notes).

**Pending:**
- Prepare/release 0.15.0 when requested; `main` already has 0.14.0.
- Then start the analyzer P0 (Flake8/Bandit/detect-secrets/profile) and SecInterp migration.

**Command to resume:**
`/start-session` (it now refreshes metrics and runs the validators).
