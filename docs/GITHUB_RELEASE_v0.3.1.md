# 🚀 QGIS Plugin Manager v0.3.1: Professional Scaffolding & UX

This version consolidates all recent advancements from the v0.3.x development effort into a polished, high-quality release. **v0.3.1** specifically addresses a critical crash discovered in the deployment progress bar.

> [!IMPORTANT]
> This is a **CLI tool**, not a QGIS plugin. Install it as a Python package using `uv` or `pip`.

## ✨ What's New in v0.3.1 (Patch)

### 🛠️ Critical Fix
- **Resolved**: Fixed `TypeError: object of type 'generator' has no len()` which caused the `deploy` command to crash when displaying the progress bar.
- **Improved**: Added regression tests to ensure robust file discovery across all supported platforms (Linux, macOS, Windows).

---

## 🌟 Highlights from v0.3.0 (Consolidated)

### 🏗️ Plugin Scaffolding
- **`init` command**: Create a complete, standardized QGIS plugin structure in seconds, including mandatory metadata, entry points, and resource templates.

### 🎮 Superior User Experience
- **Interactive Mode**: Use `--interactive` with `deploy` for step-by-step confirmation of critical actions.
- **Visual Feedback**: Modern output with real-time progress bars, color-coded messages, and emojis for immediate clarity.
- **Intelligent Hints**: Helpful suggestions ("💡 Hints") when common errors occur (like missing metadata).

### ⚙️ Automation & Configuration
- **Persistent Settings**: Support for global configuration (`~/.config/qgis-manager/config.toml`) and project-specific overrides in `pyproject.toml`.
- **Deployment Hooks**: Execute shell commands automatically before and after deployment (`pre-deploy` and `post-deploy`).
- **Advanced Logging**: Full control over verbosity levels (`-v`, `-vv`) and optional output to persistent log files.

### ✅ Validation & Reliability
- **Strict Validation**: Verify `metadata.txt` against official QGIS repository standards.
- **Safe Deployment**: Automated timestamped backups before every deployment.
- **Cross-Platform**: Full support for Linux, macOS, and Windows.

## 📦 Installation

Recomendamos el uso de `uv` para la instalación como herramienta global:

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.3.1
```

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.2.0...v0.3.1
