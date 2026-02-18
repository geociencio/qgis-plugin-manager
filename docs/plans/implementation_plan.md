# Implementation Plan: Dependency Minimization (Zero-Core-Dependency Goal)

Optimize the project by removing non-essential external dependencies and ensuring compatibility with Python 3.10+ using only the standard library.

## Proposed Changes

### [Component Name] Core Logic (src/qgis_manager)

#### [MODIFY] [ignore.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/ignore.py)
Re-implement the ignore system using `fnmatch` and `pathlib` instead of `pathspec`.
- Function `load_ignore_patterns`:
    - Read `.gitignore` and `.qgisignore`.
    - Handle `pyproject.toml` parsing using `tomllib` (3.11+) with a simple fallback for 3.10 or by using a basic regex/string parser for the specific `ignore` list.
- Class `PathFilter`:
    - Use enhanced glob matching logic to support directory-specific ignores and recursive wildcards.

#### [DELETE] [pathspec dependency](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/pyproject.toml)
Remove `pathspec` from the `dependencies` list in `pyproject.toml`.

## Verification Plan

### Automated Tests
- Run updated `tests/test_ignore_system.py` to ensure patterns are still correctly matched.
- Execute `uv run qgis-manage package` and verify zip content.

### Manual Verification
- Verify that `uv sync` no longer installs `pathspec`.
