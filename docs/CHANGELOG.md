# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Changed
- Replaced legacy flat `scaffold/` directory with structured Gen 5 blueprints (`scaffold/qgis/`, `scaffold/mining/`).
- Migrated all agent workflows from Spanish to English (`start-session`, `create-commit`, `close-session`, etc.).
- Updated `project-context` skill to reflect the CLI tool architecture (Python/Typer), not a QGIS plugin.
- Synchronized all core skills (`coding-standards`, `commit-standards`, `agentic-memory`) to English Gen 5 standard.

### Added
- New `scripts/` directory with MCP-ready agent utilities:
  - `mcp_server.py`: Model Context Protocol server implementation.
  - `skill_sync.py`: Automatic skill and workflow synchronization tool.
  - `security_scan.py`: Static security analysis utility.
- New skills: `changelog-generator`, `documentation-standards`, `domain-logic`, `qa-standards`.
- New workflows: `build-feature`, `fix-linting`, `verify-standards`, `ia-critic`.
- `QUICK_REFERENCE.md` for fast agent onboarding.
- `init_agent_system.sh` bootstrap script.

### Removed
- Domain-specific QGIS skills from core agent (`qgis-core`, `qa-docker`, `ui-framework`, `geological-logic`) — moved to `scaffold/qgis/skills/`.
- Deprecated Spanish workflows: `inicia-sesion`, `cierra-fase`, `inicia-fase`, `crea-commit`, `verificar-estandares`, `release-plugin`, etc.

---

## [0.6.4] - 2026-04-03
See [RELEASE_NOTES_v0.6.4.md](releases/RELEASE_NOTES_v0.6.4.md) for details.

## [0.6.3] - 2026-03-XX
See [v0.6.3.md](releases/v0.6.3.md) for details.
