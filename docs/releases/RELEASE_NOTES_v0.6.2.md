# Release Notes - qgis-manage v0.6.2

We are excited to announce the release of **qgis-manage v0.6.2**. This version brings significant infrastructure improvements, new CLI commands for automation, and critical stability fixes for metadata management.

## 🚀 What's New

### 🪝 Advanced Hooks System
A new `hooks` command allows you to manage and test native Python hooks without full deployment.
- `hooks list`: Catalog all available native and shell hooks.
- `hooks init`: Scaffold a `plugin_hooks.py` template.
- `hooks test [name]`: Isolated execution with mock context.

### ⬆️ Automated Versioning
The `bump` command automates Semantic Versioning across your project.
- Supports `major`, `minor`, and `patch` increments.
- `bump sync`: One-way synchronization from `pyproject.toml` to `metadata.txt`.

### 🛡️ Enhanced Stability (Critical Fixes)
- **Metadata Resilience**: Resolved issues where `ConfigParser` would lowercase CamelCase keys or crash on the `%` character.
- **Save Robustness**: Improved atomic-like saving of `metadata.txt` with better error reporting.

### 🧩 Improved Infrastructure
- **Standards Compliance**: All core modules now follow **Google Style Docstrings** and feature **Strict Typing**.
- **Logging**: Transitioned from `print` debugging to a robust `logging` architecture.
- **Validation**: Deeper structural checks with `--repo` for official QGIS repository compliance.

## 📦 Installation
Update to the latest version via `uv`:
```bash
uv tool install qgis-manage@latest
```

## 📄 Full Changelog
See [CHANGELOG.md](../../CHANGELOG.md) for a detailed list of changes.
