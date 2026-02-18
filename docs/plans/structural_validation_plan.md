# Implementation Plan: Phase 3 - Deep Structural Validation

Enhance the validation system to go beyond `metadata.txt` checks, ensuring the entire QGIS plugin project structure follows official requirements and best practices.

## User Review Required

> [!IMPORTANT]
> The validation will now check for the existence of files like `__init__.py` and icons. This might cause existing "broken" or "minimal" projects to fail validation where they previously passed only metadata checks.

## Proposed Changes

### [Component Name] Validation and Discovery (src/qgis_manager)

#### [MODIFY] [discovery.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/discovery.py)
- Import `re` which was missing and causing `slugify` to fail.
- Improve `get_plugin_metadata` to handle missing files more gracefully.

#### [MODIFY] [validation.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/validation.py)
- **Add `validate_project_structure` function**:
    - Check for `__init__.py`.
    - Check for the icon file specified in `metadata.txt` (default `icon.png`).
    - Verify that the plugin directory structure is valid for QGIS.
- **Enhance `validate_metadata`**:
    - Add checks for `qgisMaximumVersion` consistency.
    - Check for illegal characters in the name/slug.

### [Component Name] CLI (src/qgis_manager/cli/commands/validate.py)

#### [MODIFY] [validate.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/commands/validate.py)
- Update the `validate` command to run both metadata and structural validation.

## Verification Plan

### Automated Tests
- Create a `tests/test_validation.py` with various "broken" project structures (e.g., missing icon, missing `__init__.py`) and verify they are caught.

### Manual Verification
- Run `qgis-manage validate` on the current project.
- Temporarily rename `icon.png` and verify validation fails or warns.
