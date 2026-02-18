# Implementation Plan: QGIS Repository Compliance & Distribution

This plan outlines the enhancements to `qgis-plugin-manager` to make it the ultimate tool for both local development and official distribution.

## Proposed Changes

### [Distribution Engine]
Enhance the packaging logic to ensure "Repo-Ready" artifacts.

#### [MODIFY] [package.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/commands/package.py)
- Implement strict zip structure validation (single root folder).
- Add automated version syncing from `pyproject.toml` to `metadata.txt` during packaging.
- Add `--repo-check` flag to run compliance tests.

#### [MODIFY] [validate.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/commands/validate.py)
- Add checks for:
    - Valid `LICENSE` file presence and encoding.
    - Search for prohibited binary extensions (`.so`, `.dll`, `.exe`).
    - Verify `metadata.txt` field completeness (`repository`, `tracker`, etc.).

### [CI/CD Integration]
Add scaffolding for professional automation.

#### [NEW] [gh-actions-template.yml](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/scaffold/ci/github_actions.yml)
- Template for automated packaging and testing on GitHub.

## Verification Plan

### Automated Tests
- `tests/test_distribution.py`: New tests to verify repository-compliant ZIP generation.
- `tests/test_compliance_validator.py`: Verify that binary detection and metadata checks work.

### Manual Verification
- Run `qgis-manage package --repo-check` on the project.
- Inspect the generated ZIP structure.
