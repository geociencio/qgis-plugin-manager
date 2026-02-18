---
description: Unified Release Workflow for CLI Tools (PyPI Release Flow)
agent: QA Engineer
skills: [release-management, commit-standards, coding-standards]
validation: |
  - Verify that all tests pass locally (uv run pytest)
  - Confirm that ruff and mypy report no errors
  - Validate that versions are synchronized via `qgis-manage bump sync`
  - Verify that the PyPI build (Wheel/Sdist) is correct
---

Follow this 5-phase workflow to perform an official release of the `qgis-manage` tool.

### Phase 1: Quality & Readiness

🤖 **Agent Action**: Validate complete pre-release checklist.

1. **Analyze Quality**:
   // turbo
   ```bash
   uv run ruff check . && uv run mypy src/
   ```

   🤖 **Agent Action**: Verify no linting errors or static typing (Type Hints) violations.

2. **Update Badges**: Ensure `Code Quality` and `PyPI` badges in `README.md` reflect current metrics.

### Phase 2: Versioning & Documentation

🤖 **Agent Action**: Use `qgis-manage bump` for flawless semantic versioning.

1. **Sync Version**:
   // turbo
   ```bash
   # Increment version (choose: patch, minor, or major)
   uv run qgis-manage bump patch
   # Sync metadata.txt (if kept for compatibility)
   uv run qgis-manage bump sync
   ```

   🤖 **Agent Action**: Validate that `pyproject.toml` and `metadata.txt` have the exact same version.

2. **Changelog**: Update `docs/releases/RELEASE_NOTES_vX.Y.Z.md` and the main `CHANGELOG.md`.

### Phase 3: Technical Verification

1. **Final Linting**:
   // turbo
   ```bash
   uv run ruff check --fix . && uv run black .
   ```
2. **Tests**:
   // turbo
   ```bash
   uv run pytest
   ```

   🤖 **Agent Action**: Alert if any test fails or if there is regression in core functionality.

### Phase 4: Git & Tagging

1. **Preparation Commit**:
   ```bash
   git add pyproject.toml README.md docs/
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Phase 5: Build & Distribution (PyPI)

1. **Build**:
   // turbo
   ```bash
   uv build
   ```
   (Verify `.whl` and `.tar.gz` files in `dist/`).

2. **Publication**:
   ```bash
   uv publish
   ```

3. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md dist/* --draft
   ```

## Expected Outcome
- Official version available on PyPI (`pip install qgis-manage`).
- Git tag and GitHub Release created.
- Technical documentation synchronized with the new version.
