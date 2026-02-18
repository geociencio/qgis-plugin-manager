# Implementation Plan: Advanced Hooks System (`hooks`)

Introduce the `hooks` command to allow developers to manage, template, and test their project hooks in isolation.

## Proposed Changes

### [CLI]
#### [NEW] [hooks.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/commands/hooks.py)
- **`list` sub-command**:
    - Parse `pyproject.toml` for `[tool.qgis-manager.hooks]`.
    - Use `inspect` or `ast` to find functions in `plugin_hooks.py`.
    - Display in a clean table view.
- **`init` sub-command**:
    - Write a standard `plugin_hooks.py` with templates for `pre_deploy`, `post_deploy`, `pre_package`.
- **`test` sub-command**:
    - Take hook name as argument.
    - Build a mock context dictionary.
    - Execute the hook and report exit status.

### [Core]
#### [MODIFY] [hooks.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/hooks.py)
- Extract hook discovery logic into reusable functions for the CLI.

## Verification Plan
### Automated Tests
- `tests/test_cli_hooks.py`: Test all sub-commands with mock projects.
- `tests/test_hooks_init.py`: Verify generated template content.
