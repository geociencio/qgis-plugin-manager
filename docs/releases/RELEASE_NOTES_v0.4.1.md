# Release Notes v0.4.1

*31 December 2025*

This is a maintenance release that focuses on improving the packaging command to produce cleaner, more compliant ZIP files for QGIS Plugin Repository distribution.

## 🐛 Bug Fixes

*   **Fixed Nested Wildcard Exclusions**:
    *   Previously, the exclusion logic only applied wildcard patterns (like `*.egg-info` or `__pycache__`) effectively at the project root or when specifically named in the exclusion set.
    *   This update ensures that these patterns are checked against *every* component of a file's path, correctly excluding nested occurrences (e.g., `src/libs/mylib.egg-info` will now be properly excluded).

*   **Cleaner Packages**:
    *   Significantly expanded the default list of files ignored by the `package` and `deploy` commands.
    *   The tool now automatically excludes common development detritus that should not be in a production build, including:
        *   **IDE Configs**: `.vscode`, `.idea`, `.settings`, `.project`, `.classpath`.
        *   **Package Manager Locks**: `uv.lock`, `poetry.lock`, `Pipfile`, `Pipfile.lock`.
        *   **Linting/Testing Caches**: `.mypy_cache`, `.pre-commit-config.yaml`.
        *   **Internal Artifacts**: `.agent`, `.ai-context`, `analysis_results`.

## 📦 Upgrading

To update to the latest version:

```bash
uv lock --update-package qgis-plugin-manager
uv sync
```
