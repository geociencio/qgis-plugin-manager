# Active Task: Agent Framework P0 Hardening

## Status
- **Phase**: Closed
- **Progress**: 100%
- **Status**: ✅ P0 implemented and verified (2026-10-19)

## Objectives
1. [x] Bootstrap `.agent-state/memory/agent_metrics.json` with a real collector
   (`scripts/sync_metrics.py`).
2. [x] Make `forge.py memory prune` a dry-run by default (`--apply` to mutate).
3. [x] Extend the validator to scaffolds, links, canonical agent IDs, state files
   and trigger conflicts.
4. [x] Adapt start/close/test/release workflows to commands that exist in the repository.
5. [x] Dogfood the framework gates: ruff, formatting, mypy, complexity, module size and
   tooling tests.
6. [x] Add agent-system validation and tooling checks to CI.

## Todo
- [x] Metrics collector + metrics/policy/AI context files.
- [x] Safe pruning + tests.
- [x] Validator split (`agent_links`, `workflow_graph`, `skill_conflicts`,
  `frontmatter`) + tooling tests.
- [x] Framework lint/type/complexity/module-size cleanup.
- [x] CI job for `.agent` validation, lint, types and tests.
- [x] Workflow and documentation refresh.

## Context
- Framework: **agentic-forge** `.agent/` submodule **v1.4.1** (clean upstream
  release); two upstream issues (mypy TOML decode, metrics self/cache scan) are
  documented and worked around in CI until v1.4.2.
- Quality: **217 project tests**, **90.48 %** line coverage, ruff/format/mypy clean;
  **33 framework tooling tests**; CI green across Ubuntu/Windows/macOS × Python 3.11–3.13.
- Metrics: `agent_metrics.json` refreshed with `uv run python scripts/sync_metrics.py`.
- Compatibility: validated against temporary copies of `sec_interp`,
  `qgis-plugin-analyzer` and `ai-context-core` (validate, graph, conflicts, metrics,
  memory check).
- Next: see `.agent-state/next_steps.md` for the P1 backlog.
