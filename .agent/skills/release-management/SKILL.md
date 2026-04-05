---
name: release-management
description: Standards for the release process of CLI tools with quality validation.
trigger: when preparing releases, updating versions, or using the /release-plugin workflow.
---

# Release Management (CLI Tools)

Controls the lifecycle of tool versions, ensuring that each delivery meets PyPI and project quality standards.

## When to use this skill
- When finishing a development phase and preparing a new release.
- When updating `pyproject.toml` or `metadata.txt`.
- When generating release notes or updating the changelog.
- When using the `/release-plugin` workflow.

## Degree of Freedom
- **Strict**: The 5-phase process and quality requirements are non-negotiable.

## Detailed Workflow

### Phase 1: Quality and Preparation
1. **Quality Analysis**:
   ```bash
   uv run ruff check . && uv run mypy src/
   ```
   - Validate: Zero linting and typing errors.
2. **Update Badges**: Reflect metrics in `README.md` (CI, PyPI status).

### Phase 2: Versioning and Documentation
1. **Synchronization**: Use `qgis-manage bump` to update versions in `pyproject.toml` and `metadata.txt`.
2. **Semver Rules**:
   - MAJOR (X): Incompatible API changes.
   - MINOR (Y): New functionalities in a backward-compatible manner.
   - PATCH (Z): Backward-compatible bug fixes.
3. **Release Notes**: Generate in `docs/releases/RELEASE_NOTES_vX.Y.Z.md`.

### Phase 3: Technical Verification
1. Ensure 100% of tests pass via `uv run pytest`.
2. Verify CLI integrity with `uv run qgis-manage --help`.

### Phase 4: Git and Tagging
1. Release commit: `chore(release): prepare vX.Y.Z`.
2. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
3. Push: `git push origin main --tags`.

### Phase 5: Build and Distribution
1. Build: `uv build`.
2. Validate artifacts in `dist/`: `.whl` (Wheel) and `.tar.gz` (Source Distribution).
3. Publish: `uv publish` to upload to PyPI and create a GitHub release.

## Quality Checklist
- [ ] Does the code pass 100% of `ruff` and `mypy` checks?
- [ ] Was `bump` used to synchronize versions?
- [ ] Were build artifacts generated (`uv build`)?
- [ ] Were Git Tagging rules followed?
- [ ] Did all tests pass successfully?
