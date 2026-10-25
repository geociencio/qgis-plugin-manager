# Agentic Forge — Adoption & Adaptation Guide

**Date**: 2026-10-11
**Author**: @architect (+ @qa_engineer verification)
**Scope**: How to adopt the **agentic-forge** framework into a project and adapt it to
that project's domain. Companion to the migration report [`AGENTIC_FORGE_ADOPTION.md`](AGENTIC_FORGE_ADOPTION.md);
`qgis-plugin-analyzer` is the reference pilot, `qgis-plugin-manager` is the applied case.

---

## 1. Purpose

`agentic-forge` (https://codeberg.org/geociencio/agentic-forge, MIT) separates the
**re-usable framework** (skills, workflows, tooling) from **project-owned state**
(memory, task board, overlay skills). Adopting it means mounting the framework as a git
submodule and moving everything project-specific into a state directory, so framework
updates never overwrite project data and the same tooling works across sibling repos.

- **Adopt** = mount the framework + split the state (mechanical, identical for every project).
- **Adapt** = choose thresholds, overlay skills, analyzer command, agent roles and CI wiring
  (project-specific).

### Target model

```
<project>/
├── .agent/            ← git submodule → agentic-forge (pinned tag)
│   ├── skills/  workflows/  tools/  scaffold/<domain>/  AGENTS.md
├── .agent-state/      ← project-owned (never overwritten by framework updates)
│   ├── memory/  history/  task.md  next_steps.md
│   └── skills/        (overlay: project + domain skills)
├── forge.toml         ← [forge].framework/.state + [project] thresholds
├── opencode.json      ← native subagents (allow/ask/deny) + skills.paths
└── AGENTS.md          ← canonical root override (what opencode loads)
```

---

## 2. Adoption steps (F1–F5) — mechanical

### F1 — State / path split
- `git mv` `memory/`, `history/`, `task.md`, `next_steps.md` (and any project state) → `.agent-state/`.
- Add `forge.toml` (see §3.1 for values):

  ```toml
  [forge]
  framework = ".agent"        # re-usable framework (git submodule)
  state = ".agent-state"      # project-owned state

  [project]
  name = "<project>"
  test_dirs = ["tests"]
  analyzer_command = "<quality command>"
  max_cc = <n>
  module_size_limit = <n>
  ```

### F2 — Content split (overlay)
- Move project/domain-specific skills → `.agent-state/skills/` (overlay). Keep **only**
  reusable skills in the framework.
- Refresh each overlay skill so it matches reality (tooling, entry points, language).

### F3 — Submodule
- Mount the framework: `git submodule add <url> .agent` and pin the tag, e.g.
  `.agent (v1.2.0)`.
- CI: add `submodules: recursive` to **every** `actions/checkout` step.

### F4 — Tooling
- Use the framework CLI: `python .agent/tools/forge.py {validate|metrics|memory|lesson}`.
- Keep any **project-owned** generator/adapter (e.g. a CLI help generator); remove legacy
  agentic scripts (`skill_sync.py`, `validate_agent_system.py`, `memory_prune.py`,
  `mcp_server.py`, …).

### F5 — Config + docs
- `opencode.json`: `"skills": { "paths": [".agent/skills", ".agent-state/skills"] }` and the
  three native subagents (`architect`/`qa_engineer`/`auditor`) with the permission gradient
  `edit: allow|ask|deny`.
- Rewrite the root `AGENTS.md` as the single source of truth (roles, skills table, workflows
  table, `forge.py` tooling).
- Lint: exclude `.agent` and `.agent-state` (e.g. ruff `exclude`).
- Record the migration in `docs/DEVELOPMENT_LOG.md` + a session log.

---

## 3. Adaptation (project-specific)

### 3.1 `forge.toml` thresholds
Pull them from the project's own rules, not guesses. Example (manager): `max_cc = 10` and
`module_size_limit = 400`; `analyzer_command = "uv run qgis-analyzer analyze ."`.

### 3.2 Overlay skills
Onboard only what is genuinely project/domain-specific. The manager keeps **two**:
`domain-logic`, `project-context` (`9 framework + 2 overlay = 11`).

### 3.3 Analyzer command
Point `[project].analyzer_command` at the project's quality gate, so `forge` tooling and the
metrics collector run the right thing. The manager delegates analysis to
`qgis-analyzer` (it does not ship its own analyzer).

### 3.4 Agent roles / prompts
Adapt each subagent prompt to the project's architecture. Example: the manager's
`@architect` protects the separation between the **CLI** (`src/qgis_manager/`) and the
injected **runtime templates** (`src/qgis_manager/templates/`); `@qa_engineer` is
paranoid about **CLI regressions** and **template-generation edge cases**; `@auditor`
is read-only.

### 3.5 Domain scaffold
QGIS-specific skills/workflows live in the framework's `.agent/scaffold/qgis/` and are **not**
consumed unless the project opts in (mount the needed ones as overlay). This project
keeps no duplicate copy: the framework pack is the single source. Generic projects
ignore `scaffold/`.

---

## 4. Verification gates

Run after adopting; all must be green.

| Gate | Command | Expected |
| :--- | :--- | :--- |
| Agent system | `python .agent/tools/forge.py validate` | ✅ skills/workflows, no broken refs |
| Conflicts | `python .agent/tools/forge.py validate --conflicts` | ✅ no overlaps |
| Submodule | `git submodule status` | ✅ `.agent` @ pinned tag |
| Lint | `uv run ruff check .` | ✅ clean |
| Types | `uv run mypy src` | ✅ clean |
| Tests | `uv run pytest -q` | ✅ all pass |

---

## 5. Worked example — `qgis-plugin-manager`

| Aspect | Value |
| :--- | :--- |
| Framework | `.agent` submodule @ `2de22cf` (`v1.2.0`) |
| State | `.agent-state/` (`memory/`, `history/`, `skills/`) |
| `max_cc` / `module_size_limit` | `10` / `400` |
| `analyzer_command` | `uv run qgis-analyzer analyze .` |
| Skills | 11 = 9 framework + 2 overlay (`domain-logic`, `project-context`) |
| Workflows | 15 framework |
| CI | `main.yml` with `submodules: recursive` |
| Legacy removed | `scripts/{skill_sync,mcp_server,security_scan}.py` (Gen 5 sync + SecInterp leftovers) |
| Kept (project-owned) | `scripts/generate_help.py` (CLI help generator) |

---

## 6. References

- Framework repo: https://codeberg.org/geociencio/agentic-forge (MIT)
- Migration report: [`AGENTIC_FORGE_ADOPTION.md`](AGENTIC_FORGE_ADOPTION.md)
- Session log: `docs/maintenance/session_2026-10-08_agentic_forge_adoption.md`
- Unified plan: `docs/plans/implementation_plan_unify_agentic_systems.md` (sec_interp repo)
