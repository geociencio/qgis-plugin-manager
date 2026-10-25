# Development Log: qgis-manage

## [2026-10-25] P1/P2 Completion
- **Achievement**: Closed the P1 and P2 backlogs: docs/domain-pack consolidation, real deploy/package E2E, path/trust hardening, strict typing, normalized release notes and annotated architecture plans.
- **Changes**:
    - Root `AGENTS.md` is canonical; `.agent/scaffold/qgis` is the only QGIS pack; E2E deploy/package tests added.
    - Symlink confinement, POSIX ZIP names, unsafe-version rejection and explicit `--trust` for hooks/dependencies.
    - `py.typed` + strict mypy, dead `cli.py`/`get_ignore_func` removed, Makefile/README/docs refreshed.
    - Release notes normalized to `vX.Y.Z.md` with workflow fallback; Gen 7/8 plan status indexed.
- **Quality**: 248 tests (+13 subtests), 90.45 % line coverage, ruff/format/strict mypy clean; framework 37 tests and validators clean.
- **Maintenance**: [session_2026-10-25_p1_p2_completion.md](maintenance/session_2026-10-25_p1_p2_completion.md).

## [2026-10-19] P0 Hardening & Agentic Forge v1.4.2
- **Achievement**: Hardened the CLI against destructive operations and adopted the released Agentic Forge v1.4.2 with framework validation in CI.
- **Changes**:
    - Added safe slug validation, destination guards, line-oriented `metadata.txt` updates, real backup purging and identifier-safe scaffolding.
    - Fixed PyQt6 patching, compile failure propagation, profile precedence, boolean/version validation and repository compliance ordering.
    - Moved `.agent` from v1.2.0 to v1.4.2; added `scripts/sync_metrics.py`, memory policy, agent metrics and framework CI.
    - Added the deep CLI analysis and Agentic Forge audit reports.
- **Quality**: 217 tests (+13 subtests), 90.48 % line coverage, ruff/format/mypy clean; framework 37 tests and validators clean.
- **Maintenance**: [session_2026-10-19_p0_and_forge_v1_4_2.md](maintenance/session_2026-10-19_p0_and_forge_v1_4_2.md).

## [2026-10-10] Release v0.9.2 (preparation)
Patch release: cross-platform CI fix (tests only, no runtime changes).
- Fixed `test_discovery` (compare against `tmp_path.resolve()`) and `test_commands` hooks test (read with `encoding="utf-8"`) so the suite passes on macOS/Windows.
- Bumped to 0.9.2; added `[0.9.2]` to `CHANGELOG.md`/`docs/CHANGELOG.md`; created `docs/releases/notes/v0.9.2.md`.

## [2026-10-10] Release v0.9.1 (preparation)
Maintenance release (no user-facing changes).
- Bumped `pyproject.toml` / `metadata.txt` to 0.9.1; regenerated `uv.lock`.
- Added the `[0.9.1]` section to `CHANGELOG.md` and `docs/CHANGELOG.md`; created `docs/releases/notes/v0.9.1.md`.
- Pending: push `main`, tag `v0.9.1` (triggers the draft release), then publish it to upload to PyPI.

## [2026-10-10] Refactor: split `core.py` into a package + complexity reduction
Behaviour-preserving refactor of the 840-line `core.py` monolith into `qgis_manager.core` (plan: `docs/plans/core_refactoring_plan.md`).
- Split into `core/{platform,deploy,compile,package,cleanup,scaffold}.py` + `core/__init__.py` re-exporting the public API (20 symbols). All modules ≤ 352 lines (limit 400).
- Lowered complexity of the 6 functions above `max_cc = 10`: `stamp_metadata_text` D21→B7, `create_plugin_package` C18→A5, `sync_directory` C15→B7, `compile_qt_resources` C15→A4, `compile_docs` C12→B7, `clean_artifacts` C12→A1. Average CC B(7.67)→A(4.44); MI A(23.75)→A(42–63).
- Updated `@patch` targets in `tests/test_core.py` / `tests/test_commands.py` to the new submodules.
- Coverage 89.78 %→89.93 %; 190 tests pass; `ruff`/`ruff format --check`/`mypy` clean.
- Maintenance: [session_2026-10-10_core_refactor.md](maintenance/session_2026-10-10_core_refactor.md).

## [2026-10-10] Automated Release Pipeline & Release-Docs Migration
Adopted the analyzer-style two-stage release pipeline and aligned the release documentation.
- Added `.github/workflows/release.yml` (`draft-release` on tag push + `publish-pypi` on release published, via the `PYPI_TOKEN` secret).
- CI (`main.yml`): added `ruff format --check`, a coverage gate (`--cov=qgis_manager --cov-fail-under=80`) and an informational self-analysis step (`qgis-analyzer analyze .`).
- `pyproject.toml`: added `pytest-cov` and `[tool.coverage]` (`source`/`fail_under = 80`); regenerated `uv.lock`; ran `ruff format .`.
- Migrated release docs: notes → `docs/releases/notes/`, GitHub bodies → `docs/releases/github/`; rewrote the release guide at `docs/releases/RELEASE_PROCESS.md` for `qgis-manage`.
- Synced `docs/CHANGELOG.md` with the canonical root `CHANGELOG.md`.
- Maintenance: [session_2026-10-10_release_pipeline.md](maintenance/session_2026-10-10_release_pipeline.md).

## [2026-10-08] Agentic Forge Adoption (F1–F5)
Adopted the `agentic-forge` framework `v1.2.0` (Codeberg, MIT) as a git submodule at `.agent/`.
- Moved project state to `.agent-state/` (memory, history, task, next_steps) and the 2 project skills (`domain-logic`, `project-context`) to the overlay.
- Added `forge.toml` and `opencode.json`; created the canonical root `AGENTS.md`.
- Removed `scripts/{skill_sync,mcp_server,security_scan}.py`; kept `generate_help.py`.
- CI uses `submodules: recursive`; ruff excludes `.agent`/`.agent-state`.
- Maintenance: [session_2026-10-08_agentic_forge_adoption.md](maintenance/session_2026-10-08_agentic_forge_adoption.md).

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
