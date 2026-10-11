# Active Task: CLI Validation and Linting Fix

## Status
- **Phase**: Implementation
- **Progress**: 60%
- **Status**: 🟢 Healthy

## Objectives
1. [x] **Support QGIS 4 and Multi-version**: Eliminated hardcoded QGIS 3 paths and added `--qgis-version` support.
2. [ ] **Validate CLI Integrations**: Ensure Typer commands correctly handle the new blueprints in `/scaffold`.
3. [ ] **Resolve Scripts Linting**: Fix or ignore `ruff` violations in the `scripts/` directory.

## Todo
### QGIS 4 Support (Completed)
- [x] Update `Settings` class in `config.py`.
- [x] Update path detection in `core.py`.
- [x] Add `--qgis-version` to `deploy` command.
- [x] Implement interactive path validation.
- [x] Update and run tests.

### CLI Validation
- [ ] List current Typer commands.
- [ ] Test `scaffold` command with different blueprints (`qgis`, `mining`).
- [ ] Verify generated files match expectations.

### Linting Fix
- [ ] Run `ruff check scripts/` to see current violations.
- [ ] Update `pyproject.toml` to exclude `scripts/` from ruff checks (as per Lesson 2026-04-05).
- [ ] Verify `make lint` passes without errors.

## Context
- The project recently migrated to Gen 5 architecture.
- `scripts/` contains inherited utilities that don't follow the main project's line-length standards.
- `scaffold/` structure was recently updated to be more modular.
