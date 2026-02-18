# Implementation Plan: Automated Versioning (`bump`)

Introduce the `bump` command to centralize version management across `pyproject.toml`, `metadata.txt`, and source code.

## Proposed Changes

### [CLI]
#### [NEW] [bump.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/commands/bump.py)
- **`major / minor / patch` sub-commands**:
    - Fetch current version from `pyproject.toml` (Primary Source).
    - Parse using semantic versioning rules.
    - Increment and update all relevant files.
- **`sync` sub-command**:
    - Propagate `pyproject.toml` version to `metadata.txt`.
- **`--check` flag**:
    - Compare all version markers and fail if mismatched.

### [Core]
#### [MODIFY] [discovery.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/discovery.py)
- Add utility to update `pyproject.toml` [project].version using `tomllib` (read) and `tomlkit` or regex-safe replacement (write) to preserve comments.

## Verification Plan
### Automated Tests
- `tests/test_version_bumping.py`: Verify increments (0.6.0 -> 0.6.1, etc.).
- `tests/test_version_sync.py`: Verify propagation to `metadata.txt`.
