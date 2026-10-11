# Release Notes - qgis-manage v0.8.0 - Python 3.11+ and Structured Help

We are excited to announce the release of **qgis-manage v0.8.0**. This minor release modernizes the codebase (Python 3.11+), centralizes TOML handling, fixes the interactive deploy path, and introduces a structured `--help` output with a generated command reference.

## 🚀 Key Features

### 📖 Structured Help
Every command now renders a consistent, structured `--help` template with a title, description, usage, subcommands/options, and usage examples.

```text
qgis-manage v0.8.0
QGIS Plugin Manager - Modern CLI for plugin development.

Usage: qgis-manage ... SUBCOMMAND ...

Subcommands:
  deploy      Deploy the plugin to the local QGIS profile
  ...

General Options:
  -h, --help    show this help message and exit
  ...
```

The full command reference is also available as static Markdown files in [`help/`](help/). Regenerate them with `make help`.

### 🐍 Python 3.11+
The minimum Python version is now 3.11. All `tomli` fallbacks were replaced with the standard-library `tomllib`.

## 🛠️ Improvements

- **Centralized TOML handling**: New `toml_utils.py` with `load_toml`, `get_project_version` and `set_project_version`, replacing fragile regex-based version editing.
- **Version sync**: `sync_metadata_version` in `discovery.py`, reused by `bump` and `package`.
- **Progress bars**: Extracted the duplicated compile progressbar callback into `cli/progress.py`.
- **RCC detection**: `get_rcc_tool` now uses `shutil.which` instead of running `--version`.
- **Hooks convention**: Unified hook names to underscore (`pre_deploy`/`post_deploy`).
- **Validation**: `package --repo-check` now also runs `validate_project_structure`.
- **Testing**: Added `pytest` and raised test coverage to ~90% (163 tests).

## 🐛 Bug Fixes

- **Custom deploy path**: `deploy` now respects the interactive/manual target directory instead of ignoring it.
- **Hooks CLI**: `hooks test <hook_name>` now parses correctly via the `--path` option.

## 📦 Installation

```bash
uv tool install qgis-manage@latest
# or
pip install qgis-manage==0.8.0
```

## 📄 Full Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for a complete list of changes.
