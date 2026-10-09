# Agentic Forge Adoption — Migration Report

**Date**: 2026-10-08
**Author**: @architect (+ @qa_engineer verification)
**Scope**: Migrate qgis-plugin-manager's agentic system onto the **agentic-forge** framework.

---

## 1. Context

qgis-plugin-manager sat at **Gen 5** (Antigravity/"Gentleman Programming"): no
`opencode.json`, no `forge.toml`, canonical `.agent/AGENTS.md`, and an active
`skill_sync.py`. It was migrated onto the **agentic-forge** framework
(https://codeberg.org/geociencio/agentic-forge, MIT), separating the re-usable
framework (git submodule at `.agent/`) from project-owned state (`.agent-state/`).

### Target model

```
qgis-plugin-manager/
├── .agent/           ← git submodule → agentic-forge v1.2.0
├── .agent-state/     ← project-owned state + overlay skills
├── forge.toml        ← [forge].framework/.state + [project] thresholds
├── opencode.json     ← native subagents (allow/ask/deny) + skills.paths
└── AGENTS.md         ← canonical root override (created)
```

---

## 2. What was done (F1–F5)

### F1 — State/path split
- Moved `memory/`, `history/`, `task.md`, `next_steps.md` → `.agent-state/` (`git mv`).
- Added `forge.toml`:
  ```toml
  [forge]
  framework = ".agent"
  state = ".agent-state"

  [project]
  name = "qgis-plugin-manager"
  test_dirs = ["tests"]
  analyzer_command = "uv run qgis-analyzer analyze ."
  max_cc = 10
  module_size_limit = 400
  ```

### F2 — Content split
- Moved 2 project-specific skills to the overlay `.agent-state/skills/`:
  `domain-logic`, `project-context`.
- Fixed stale `project-context` (Typer → click, Antigravity Gen 5 → agentic-forge).

### F3 — Submodule
- `.agent/` became a git submodule of `agentic-forge`, pinned at `v1.2.0` (`2de22cf`).
- CI (`main.yml`): `submodules: recursive`.

### F4 — Tooling
- Removed `scripts/{skill_sync,mcp_server,security_scan}.py` (Gen 5 sync + SecInterp
  leftovers); kept `scripts/generate_help.py` (the manager's own CLI help generator).

### F5 — Config + docs
- Created the canonical root `AGENTS.md` and `opencode.json` (native subagents).
- `pyproject.toml`: ruff now excludes `.agent` and `.agent-state`.
- Updated `docs/DEVELOPMENT_LOG.md` and added the session log.

---

## 3. Verification (gates)

| Gate | Result |
| :--- | :--- |
| `python .agent/tools/forge.py validate` | ✅ 11 skills (9 framework + 2 overlay), 14 workflows |
| `python .agent/tools/forge.py validate --conflicts` | ✅ no overlaps |
| `git submodule status` | ✅ `.agent` @ `v1.2.0` |
| `uv run ruff check .` | ✅ clean |
| `uv run mypy src` | ✅ 30 files, no issues |
| `uv run pytest -q` | ✅ 190 passed |

---

## 4. References

- Framework repo: https://codeberg.org/geociencio/agentic-forge (MIT)
- Session log: `docs/maintenance/session_2026-10-08_agentic_forge_adoption.md`
- Unified plan: `docs/plans/implementation_plan_unify_agentic_systems.md` (sec_interp repo)
