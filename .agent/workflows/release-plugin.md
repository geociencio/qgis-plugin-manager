---
description: Perform an official release of the qgis-plugin-manager CLI tool (PyPI + GitHub).
agent: QA Engineer
skills: [release-management, changelog-generator, commit-standards, qa-standards]
validation: |
  - Verify that ruff and mypy pass without errors
  - Confirm that all tests pass (uv run python -m unittest discover tests)
  - Validate that versions are synchronized in pyproject.toml, metadata.txt and README.md
  - Ensure the changelog entry is moved from [Unreleased] to the new version
  - Confirm that uv build produces both .whl and .tar.gz in dist/
---

# Workflow: Release Plugin

Follow this 5-phase workflow to perform an official release of the `qgis-plugin-manager`
CLI tool. This workflow is adapted for a Python CLI tool (not a QGIS plugin): it relies on
`ruff`/`mypy` for quality, `qgis-manage bump` for versioning, `uv build` for packaging and
`uv publish` for distribution to PyPI.

### Phase 1: Quality and Preparation

🤖 **Agent Action**: Use the **release-management** skill to validate the pre-release checklist.

1. **Lint and type check**:
   // turbo
   ```bash
   uv run ruff check .
   uv run mypy src
   ```

   🤖 **Agent Action**: Zero linting and typing errors are required to proceed. `mypy` should
   target `src` (the packaged code); pre-existing issues in `tests/` and `scripts/` are tracked
   separately and must not block a patch release.

2. **Update badges**: Reflect current metrics in `README.md` (CI, PyPI version, code quality).

### Phase 2: Versioning and Documentation

🤖 **Agent Action**: Use the **release-management** skill to synchronize versions automatically.

1. **Bump version (Semantic Versioning)**:
   ```bash
   uv run qgis-manage bump patch   # or minor / major
   uv run qgis-manage bump sync    # sync metadata.txt from pyproject.toml
   ```

   🤖 **Agent Action**: Confirm that the three sources match exactly:
   - `version` in `pyproject.toml` (`[project]`)
   - `version` in `metadata.txt`
   - the version badge in `README.md`

2. **Changelog (Keep a Changelog)**: Use the **changelog-generator** skill to move `[Unreleased]`
   into the new version section in `CHANGELOG.md`, using valid types (`Added`, `Changed`,
   `Fixed`, `Removed`).

3. **Release notes**: Generate structured release notes in
   `docs/releases/RELEASE_NOTES_vX.Y.Z.md`.

### Phase 3: Technical Verification

🤖 **Agent Action**: Use the **qa-standards** skill to validate tests and CLI integrity.

1. **Run the test suite**:
   // turbo
   ```bash
   uv run python -m unittest discover tests
   ```

2. **Verify CLI integrity**:
   // turbo
   ```bash
   uv run qgis-manage --version
   uv run qgis-manage --help
   ```

   🤖 **Agent Action**: Alert if any test fails or if a regression is introduced.

### Phase 4: Git and Tagging

🤖 **Agent Action**: Use the **commit-standards** skill for the commit message.

1. **Preparation commit**:
   ```bash
   git add pyproject.toml metadata.txt CHANGELOG.md README.md docs/releases/RELEASE_NOTES_vX.Y.Z.md
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tag and push**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin main --tags
   ```

### Phase 5: Build and Distribution

🤖 **Agent Action**: Use the **release-management** skill to validate artifacts and publication.

1. **Build artifacts**:
   // turbo
   ```bash
   uv build
   ```
   (Verify both `dist/*.whl` and `dist/*.tar.gz` are generated.)

2. **Publish to PyPI (manual)**:
   The user performs the PyPI publication manually in the terminal. Do NOT run this
   automatically — pause here and hand off to the user.
   ```bash
   uv publish
   ```

   🤖 **Agent Action**: Wait for the user to confirm that the publication to PyPI
   completed successfully before proceeding.

3. **GitHub release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md --draft
   ```

## Expected Result
- New version published on PyPI and tagged on GitHub.
- `pyproject.toml`, `metadata.txt` and `README.md` versions synchronized.
- Changelog and release notes updated.
- Technically validated release with visible metrics.
