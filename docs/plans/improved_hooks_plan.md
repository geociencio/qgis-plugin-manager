# Implementation Plan: Phase 5 - Improved Hooks Architecture

Enable advanced automation by allowing Python-based hooks that run within the `qgis-manage` process, providing direct access to project context.

## Proposed Changes

### [Component Name] Hooks System (src/qgis_manager/hooks.py)

#### [MODIFY] [hooks.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/hooks.py)
- **Implement `execute_python_hook(project_root: Path, hook_name: str, context: dict) -> bool`**:
    - Look for `plugin_hooks.py` in `project_root`.
    - Dynamically import the module using `importlib`.
    - Check for a function named `hook_name` (normalized, e.g., `pre_deploy`).
    - Execute it and return its result (assume success if it returns `None` or `True`).
- **Refactor `run_hook`**:
    - It should now try to find a native Python hook in `plugin_hooks.py` first.
    - If not found or not applicable, fall back to the configured command (shell or script).

### [Component Name] Deployment and Packaging (src/qgis_manager/core.py)

#### [MODIFY] [core.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/core.py)
- Ensure all relevant functions that call hooks pass a comprehensive context (project root, metadata, destination paths, etc.).

## Verification Plan

### Automated Tests
- Create `tests/test_hooks_native.py`:
    - Test discovering and executing functions from a mock `plugin_hooks.py`.
    - Verify that the context is correctly passed.
    - Verify that return values from Python hooks are respected.

### Manual Verification
- Create a `plugin_hooks.py` in the current project with a `pre_deploy` function that prints a message or touches a file.
- Run `qgis-manage deploy` and verify the hook executes.
