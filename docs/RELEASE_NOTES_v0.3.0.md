# 🚀 QGIS Plugin Manager v0.3.0

A professional CLI tool for managing QGIS plugin development, deployment, and packaging. This version consolidates all recent advancements into a single, high-quality release.

> [!IMPORTANT]
> This is a **CLI tool**, not a QGIS plugin. Install it as a Python package using `uv` or `pip`.

## 📦 Installation

### Using uv (Recommended)

```bash
# Install as a global tool
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.3.0

# Or add to your project's dev dependencies
uv add --group dev qgis-plugin-manager @ git+https://github.com/geociencio/qgis-plugin-manager.git@v0.3.0
```

## ✨ What's New in v0.3.0

### 🏗️ Plugin Scaffolding
- **`init` command**: Create a complete, standardized QGIS plugin structure in seconds.
- Includes mandatory metadata, entry points, and resource templates.

### 🎮 Superior User Experience
- **Interactive Mode**: Use `--interactive` with `deploy` for step-by-step confirmation of critical actions.
- **Visual Feedback**: Real-time progress bars for file operations and ZIP packaging.
- **Modern Output**: Color-coded messages and emojis for immediate clarity on command status.

### ⚙️ Automation & Configuration
- **Persistent Settings**: Global configuration (`~/.config/qgis-manager/config.toml`) and project-specific overrides.
- **Deployment Hooks**: Execute shell commands automatically before and after deployment (`pre-deploy`/`post-deploy`).
- **Advanced Logging**: Verbosity levels (`-v`, `-vv`) and optional output to log files.

### ✅ Validation & Reliability
- **Strict Validation**: Ensure your plugins are ready for the official QGIS repository.
- **Safe Deployment**: Automated backups and secure file copying.
- **Full Test Suite**: 40 unit tests ensuring 100% stability.

## 🛠️ Usage

```bash
# Start a new project
qgis-manage init "Mi Plugin" --author "Juan" --email "juan@gmail.com"

# Deploy interactively
qgis-manage deploy --interactive

# Create a redistributable package
qgis-manage package
```

## 📊 Quality Metrics

- **Code Score**: 92.5/100 (Bright Green)
- **Test Coverage**: 40/40 tests passing
- **Python Support**: 3.10 through 3.13
- **Platforms**: Linux, macOS, Windows

## 📄 License

GPL-2.0-or-later

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/blob/main/CHANGELOG.md
