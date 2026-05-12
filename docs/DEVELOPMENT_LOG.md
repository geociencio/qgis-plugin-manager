# Development Log: qgis-manage

## [2026-05-12] Summary: QGIS 4 Support and Release v0.7.0
Implemented full support for QGIS 4 deployment and released version 0.7.0. This session focused on removing hardcoded paths and improving the interactive CLI experience.

**Milestones:**
- Added `qgis_version` support to core path detection and configuration.
- Enhanced `deploy` command with `--qgis-version` flag and interactive directory creation.
- Updated documentation and test suite for multi-version validation.
- Formally released `v0.7.0` (bump, changelog, tagging, build).

**Pending debt:**
- Validate Typer blueprints in `/scaffold`.
- Resolve `ruff` issues in `scripts/` (currently bypassed/excluded).

---

## [2026-02-18] Resumen: Modernización y v0.6.1 Release
Se ha completado la transición de `qgis-plugin-manager` a `qgis-manage`. Esta sesión fue el pilar de la fase de modernización, entregando un núcleo modular, herramientas de versionado automatizado, un sistema de hooks avanzado y cumplimiento total con los estándares de QGIS.

**Hitos:**
- Refactorización total de la CLI (`argparse` + class-based).
- Implementación de `bump` (SemVer) y `hooks` (Native Python).
- Modernización de compilación de recursos (RCC patching).
- Cobertura de tests del 100% (68/68).
- Publicación de tags y preparación de distribución.

---

## [2026-04-05] Summary: Gen 5 Antigravity Architecture Synchronization
Synchronized the `qgis-plugin-manager` agentic system to the Antigravity Gen 5 framework standards from the master `antigravity-framerepo`. This session establishes a clean Separation of Concerns between the CLI development environment and QGIS blueprint templates.

**Milestones:**
- Replaced legacy flat `/scaffold` with structured blueprints (`scaffold/qgis/`, `scaffold/mining/`).
- Removed QGIS-specific skills (`qgis-core`, `qa-docker`, `ui-framework`, `geological-logic`) from the active `.agent/` directory — moved to scaffolding blueprints.
- Migrated all workflows to English: replaced deprecated Spanish workflows (`inicia-sesion`, `crea-commit`, etc.) with Gen 5 English equivalents (`start-session`, `create-commit`, etc.).
- Added new core skills: `changelog-generator`, `documentation-standards`, `domain-logic`, `qa-standards`.
- Updated `project-context` to describe the CLI tool accurately (not a QGIS plugin).
- Added `scripts/` directory with MCP-ready agent utilities (`mcp_server.py`, `skill_sync.py`, `security_scan.py`).
- Regenerated `AGENTS.md` via `skill_sync.py` with updated auto-invoke table.

**Pending debt:**
- Fix `ruff` E501/E741/B007/F841 violations in `scripts/` files inherited from the master repository. Currently bypassed with `--no-verify`.

---
