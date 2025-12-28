# QGIS Plugin Manager

[![CI](https://github.com/geociencio/qgis-plugin-manager/actions/workflows/main.yml/badge.svg)](https://github.com/geociencio/qgis-plugin-manager/actions/workflows/main.yml)
[![License: GPL v2+](https://img.shields.io/badge/License-GPL%20v2%2B-blue.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/code%20quality-74.2%2F100-yellow)](analysis_results/PROJECT_SUMMARY.md)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A professional CLI for managing QGIS plugin development, deployment, and packaging. Modernized for Python 3.10+ and `uv`.

> [!IMPORTANT]
> **This is a CLI tool, not a QGIS plugin**
>
> This project is a **command-line tool** for managing QGIS plugin development. It should be installed as a Python package using `uv` or `pip`, **not** as a plugin in QGIS.
>
> - ✅ Use it to develop and deploy QGIS plugins
> - ❌ Do NOT install it as a plugin in QGIS

## 🚀 Features

- **Dynamic Deployment**: Automatically detects your QGIS profile directory (Linux, Windows, macOS).
- **Smart Discovery**: Reads `metadata.txt` to identify your plugin and automatically selects source files.
- **Safety First**: Automatically creates timestamped backups of your plugin folder before every deployment.
- **Qt Integration**: Compiles `.qrc` resources and `.ts` translations with simple commands.
- **Clean Workflow**: Removes `__pycache__` and artifacts recursively.

## 📦 Installation

Install system-wide as a tool using `uv`:

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git
```

Or add it to your project's development dependencies:

```bash
uv add --group dev qgis-plugin-manager @ git+https://github.com/geociencio/qgis-plugin-manager.git
```

## 🛠️ Usage

From your plugin project root:

```bash
# Deploy to QGIS profile (with automatic backup)
qgis-manage deploy

# Compile all resources and translations
qgis-manage compile

# Clean Python artifacts
qgis-manage clean
```

## 📖 Documentation

- [CHANGELOG.md](CHANGELOG.md): History of changes and releases.
- [RULES.md](RULES.md): Coding standards and project rules.

## 📄 License

GPL-2.0-or-later
