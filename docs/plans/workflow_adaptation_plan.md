# Implementation Plan: Workflow Adaptation (Tool vs Plugin)

Adapt the project's release workflows (`release-plugin.md` and `release-plugin-en.md`) to reflect that `qgis-plugin-manager` is a Python CLI tool, not a QGIS plugin.

## Proposed Changes

### [Workflows]

#### [MODIFY] [.agent/workflows/release-plugin.md](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/release-plugin.md)
#### [MODIFY] [.agent/workflows/release-plugin-en.md](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/release-plugin-en.md)
- **Phase 1**: Replace `qgis-analyzer` with general linting/typing checks (`ruff`, `mypy`).
- **Phase 2**: Use `qgis-manage bump` instead of manual editing of `metadata.txt`.
- **Phase 5**: 
    - Replace ZIP creation with `uv build` (Wheel & Sdist).
    - Replace `plugins.qgis.org` with PyPI publication (`uv publish`).
    - Remove QGIS Repository specific validations.

## Verification Plan
### Manual Verification
- Review the new workflows to ensure they cover all steps for a professional PyPI release.
- Verify that the `bump` command usage is correct.
