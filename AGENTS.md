# qgis-plugin-manager Development Guidelines for AI Agents

This document provides the essential guidelines for agentic coding agents working on the **qgis-plugin-manager** codebase — a modern CLI tool for managing QGIS plugin development (lifecycle, versioning, scaffolding, deployment, and testing). It covers build commands, code style, architectural principles, and development workflows.

This file is the **single source of truth for this project's agent configuration** (roles, build/test commands, architecture, quality gates and project overlay skills). The re-usable framework (`agentic-forge`) is mounted as a git submodule at `.agent/`; its generic defaults live in [`.agent/AGENTS.md`](.agent/AGENTS.md) and [`.agent/QUICK_REFERENCE.md`](.agent/QUICK_REFERENCE.md) and are **referenced, not duplicated, here**. Project-owned state and overlay skills live under `.agent-state/`.

---

## 🧑‍💻 Agent Roles

The agent adopts one of three roles depending on the task. Roles are registered as native subagents in `opencode.json` with a permission gradient: `architect` (`edit: allow`), `qa_engineer` (`edit: ask`), `auditor` (`edit: deny`).

### 🏗️ Senior Architect (@architect)
- **Role**: Senior Software Architect expert in Python and QGIS plugin tooling.
- **Goal**: Protect the clean separation between the manager CLI (`src/qgis_manager/`) and the injected plugin templates (`scaffold/`), and design rock-solid features.
- **Traits**: Extremely strict with SOLID principles. Prioritizes modularity and decoupling.
- **Constraint**: NEVER modify template/scaffold content while working on CLI logic. ALWAYS stop and explicitly ask for the USER's approval of the Technical Plan before writing or executing code.
- **Skills**: [coding-standards](.agent/skills/coding-standards/SKILL.md), [domain-logic](.agent-state/skills/domain-logic/SKILL.md), [documentation-standards](.agent/skills/documentation-standards/SKILL.md)

### 🧪 QA & Automation Engineer (@qa_engineer)
- **Role**: Testing, Continuous Integration, and Stability Specialist.
- **Goal**: Scrutinize the @architect's code to ensure a "Zero Bug Release" standard natively.
- **Traits**: Paranoid about CLI regressions, unhandled exceptions, and template-generation edge cases.
- **Constraint**: Focuses on finding, fixing, and validating code, rarely proposing entirely new abstractions. Full test coverage is the gold standard.
- **Skills**: [commit-standards](.agent/skills/commit-standards/SKILL.md), [coding-standards](.agent/skills/coding-standards/SKILL.md), [testing-standards](.agent/skills/testing-standards/SKILL.md)

### 🕵️ Agent Auditor (@auditor)
- **Role**: AI technical auditor specializing in architectural rigor and standards compliance.
- **Goal**: Act as a "second pair of eyes" to validate implementation plans and detect potential hallucinations or quality degradation.
- **Traits**: Neutral and critical. Scrutinizes plans proposed by other agents heavily. Acts as a **"Hallucination Hunter"**, verifying every file path and tool call.
- **Constraint**: Allows NO deviation from `ruff`, `mypy`, `uv`, or established architectural boundaries. Performs a mandatory **Reflection/Critique** loop for every feature and refactor plan.
- **Skills**: [coding-standards](.agent/skills/coding-standards/SKILL.md), [project-context](.agent-state/skills/project-context/SKILL.md), [agentic-memory](.agent/skills/agentic-memory/SKILL.md)

---

## 🧭 Workflow Commands (slash commands)

When the user types `/name`, read the corresponding `.agent/workflows/name.md`
(or `.agent-state/workflows/name.md` for a project overlay) and execute its steps.
Do NOT treat slash commands as unknown.

The canonical command list, agent/skill mapping and purposes live in the framework
index: [`.agent/workflows/index.md`](.agent/workflows/index.md). Do not duplicate that
table here; this project currently has no workflow overlay.

---

## 🚀 Build/Lint/Test Commands

### Environment setup
```bash
uv sync                              # Install dependencies (dev group)
uv run qgis-manage --version         # Verify the CLI entry point
```

### Code quality
```bash
uv run ruff check .                  # Lint
uv run ruff check --fix .            # Auto-fix lint issues
uv run ruff format .                 # Format
uv run mypy src                      # Static type checking
```

### Testing
```bash
uv run pytest -q                     # Full test suite
uv run pytest tests/test_core.py -q  # Single module
```

### CLI operations
```bash
uv run qgis-manage deploy            # Deploy to the QGIS plugins directory
uv run qgis-manage clean             # Clean build artifacts
uv run qgis-manage bump --help       # Version bumping
```

### Release
```bash
uv build && uvx twine check dist/*
```

---

## 🏗️ Architectural Principles

### CLI / Template Separation (CRITICAL)
The manager is a **CLI tool** that generates and manages QGIS plugins. It must keep two concerns strictly separated:

1. **The CLI** (`src/qgis_manager/`): command parsing (click), dispatch, and business logic. No template content lives here.
2. **Runtime templates** (`src/qgis_manager/templates/`): the files `init` renders for a new plugin (`default`, `processing`, `dockwidget`).
3. **Domain blueprints**: project-owned mining skills live in `scaffold/mining/`;
   the QGIS pack is framework-only at `.agent/scaffold/qgis/`.

#### NEVER do this:
```python
# ❌ FORBIDDEN - template content hard-coded in the CLI
def create_plugin(name: str):
    template = "class Plugin: ..."   # belongs in templates/, not the CLI
```

#### ALWAYS do this:
```python
# ✅ CORRECT - load runtime template content from src/qgis_manager/templates/
def create_plugin(name: str, template: str = "default"):
    content = (TEMPLATES_DIR / template / "plugin.py.tmpl").read_text()
    return content.format(name=name)
```

### CLI layering
- `cli/` (click layer) must stay thin: parse args → dispatch to services.
- Business logic lives in `core/`-style services, never in the click command handlers.

---

## 📝 Code Style Guidelines

- **pathlib** over `os.path` for all new path handling.
- **Google-style docstrings** on all public APIs.
- **Strict typing**: type hints on all function signatures and returns.
- **Ruff** is the single formatter/linter (`line-length = 88`, `target-version = py311`).
- Import order: stdlib → third-party → local (absolute imports `from qgis_manager...`).

```python
from __future__ import annotations

from pathlib import Path
from typing import Optional

from qgis_manager.core.discovery import discover_plugins


def discover(root: Path) -> list[Path]:
    """Discover QGIS plugins under a root directory.

    Args:
        root: Directory to scan for plugins.

    Returns:
        List of plugin directories found.
    """
```

---

## 🛠️ Agent Skills

Framework skills are defined and indexed in
[`.agent/QUICK_REFERENCE.md`](.agent/QUICK_REFERENCE.md)
and [`.agent/AGENTS.md`](.agent/AGENTS.md). Read the linked `SKILL.md` on demand;
do not pre-load all of them or duplicate the framework table here.

### Project overlay skills (manager-specific)

| Skill | Description |
| :--- | :--- |
| [domain-logic](.agent-state/skills/domain-logic/SKILL.md) | Business rules, data validation, and 3-level validation. |
| [project-context](.agent-state/skills/project-context/SKILL.md) | Purpose, architecture, and structure of qgis-plugin-manager. |

> QGIS-domain skills/workflows (`qgis-core`, `qgis-migration-4x`, `ui-framework`,
> `release-plugin`, ...) live only in the framework's
> [`.agent/scaffold/qgis/`](.agent/scaffold/qgis/README.md). This project keeps no
> duplicate QGIS pack; overlay the files you need.

---

## 🛡️ Quality Gates

This project enforces:

- **Ruff**: `ruff check .` and `ruff format .` pass with zero errors.
- **Mypy**: `mypy src` passes.
- **Pytest**: full suite passes (including `.agent/tests/`).
- **Agent tooling**: `uv run bash .agent/scripts/ci.sh` passes (framework lint,
  format, mypy, 37 tests and validators).
- **Conventional Commits**: `type(scope): description` in English.

### Agent system validation
Framework tooling, generic gates and their full command list are documented in
[`.agent/QUICK_REFERENCE.md`](.agent/QUICK_REFERENCE.md). Project-owned
validation:

```bash
uv run bash .agent/scripts/ci.sh        # framework lint/format/mypy/tests/validators
uv run python scripts/sync_metrics.py   # refresh agent_metrics.json
uv run python .agent/tools/forge.py metrics validate   # metric consistency
```

---

## 🧠 Memory Model (3-tier)

- **Working**: `AI_CONTEXT.md`, `.agent-state/next_steps.md`, `.agent-state/task.md`.
- **Episodic**: `docs/maintenance/` session logs + `.agent-state/history/`.
- **Semantic**: `.agent-state/memory/AGENT_LESSONS.md` + `SKILL.md` files.

Policy: `.agent-state/memory/memory_policy.md`. Lessons older than 90 days that are already reflected in a `SKILL.md` are pruned by `forge memory prune --apply`; without `--apply` the command is a dry-run.

---

## 🧩 Paths & Configuration

- `forge.toml` declares `[forge].framework = ".agent"` and `[forge].state = ".agent-state"`.
- Framework content (skills, workflows, tooling) lives in the `.agent/` git submodule (`agentic-forge`).
- Project-owned state and overlay skills live in `.agent-state/`, never in the submodule.

---

## 📚 Key Resources

- **Agent Configuration**: this file (root `AGENTS.md`) — canonical for this project
- **Framework defaults**: [`.agent/AGENTS.md`](.agent/AGENTS.md) and
  [`.agent/QUICK_REFERENCE.md`](.agent/QUICK_REFERENCE.md)
- **Skills**: `.agent/skills/*/SKILL.md` + `.agent-state/skills/*/SKILL.md`
- **Workflows**: `.agent/workflows/*.md` (index: `.agent/workflows/index.md`)
- **Development log**: `docs/DEVELOPMENT_LOG.md`

---

## ⚠️ Critical Reminders

1. **NEVER** hard-code template content in the CLI — runtime templates belong in
   `src/qgis_manager/templates/`; domain blueprints live in `scaffold/` or `.agent/`.
2. **ALWAYS** keep the click layer thin (parse → dispatch).
3. **USE** type annotations and Google docstrings everywhere.
4. **RUN** `ruff check . && mypy src && pytest` before committing.
5. **PRESERVE** the CLI/template separation.

This project maintains high architectural standards to ensure long-term maintainability. Respect these principles in all contributions.
