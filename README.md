# QGIS Plugin Manager

[![PyPI version](https://img.shields.io/pypi/v/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![Python versions](https://img.shields.io/pypi/pyversions/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![CI](https://github.com/geociencio/qgis-plugin-manager/actions/workflows/main.yml/badge.svg)](https://github.com/geociencio/qgis-plugin-manager/actions/workflows/main.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/geociencio/qgis-plugin-manager/graphs/commit-activity)
[![License: GPL v2+](https://img.shields.io/badge/License-GPL%20v2%2B-blue.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](https://github.com/geociencio/qgis-plugin-manager)
[![GitHub stars](https://img.shields.io/github/stars/geociencio/qgis-plugin-manager.svg?style=social&label=Star)](https://github.com/geociencio/qgis-plugin-manager/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/geociencio/qgis-plugin-manager.svg?style=social&label=Issue)](https://github.com/geociencio/qgis-plugin-manager/issues)

**QGIS Plugin Manager** is a professional, high-performance CLI tool designed to manage the full lifecycle of QGIS plugins. From local development and smart synchronization to official repository compliance and automated versioning. Now available on **PyPI** for easy integration.

---

## ✨ Features

### ⚡ Smart Synchronization
Deploy with idempotent, rsync-like sync: only changed files are copied (compared by size + mtime), and files removed from the source are cleaned up in the target. No more slow "delete and copy".

```bash
qgis-manage deploy
```

### 🗄️ Backup Rotation & Multi-profile
Every deploy creates a timestamped backup of the previous installation, with automatic rotation to keep only the N most recent. Target specific profiles or QGIS versions.

```bash
qgis-manage deploy --profile production --qgis-version 4
qgis-manage deploy --purge-backups
```

### 🪝 Native Python Hooks
Automate your workflow in pure Python via `plugin_hooks.py` — or shell commands. Hooks receive full project context (metadata, paths, profiles).

```python
# plugin_hooks.py
def pre_deploy(context):
    print("Deploying to", context["target_path"])

def post_deploy(context):
    print("Deployed", context["metadata"]["name"])
```

```bash
qgis-manage hooks list
qgis-manage hooks test pre_deploy
```

### 🎨 Resource & UI Compilation
Compile `.ui` (pyuic), `.qrc` (rcc), and `.ts` (lrelease) files — with dynamic tool detection and QGIS-compatible import patching — plus Sphinx documentation.

```bash
qgis-manage compile
```

### 🔢 Automated Versioning
Bump versions across `pyproject.toml` and `metadata.txt` with a single command.

```bash
qgis-manage bump patch
qgis-manage bump sync
```

### 📦 Packaging, Stamping & Compliance
Build repo-ready ZIPs, run compliance checks before upload, and stamp build metadata (git SHA, commit number, datetime, experimental) into `metadata.txt`.

```bash
qgis-manage package --repo-check --sync-version --stamp
```

### ✅ Deep Validation
Validate metadata and project structure against the official QGIS repository rules — catch errors *before* you upload.

```bash
qgis-manage validate --strict --repo
```

### 🌍 Smart Path Detection
Automatically detects the QGIS plugins directory across Linux, macOS and Windows for QGIS 3 and 4, with an interactive fallback when the profile does not exist.

### 📖 Structured Help
Every command ships a structured `--help` (usage, options, examples), and the full reference is generated into the [`help/`](help/) directory.

---

## 📦 Installation

Requires **Python 3.11+**.

Install system-wide using `uv` (recommended):
```bash
uv tool install qgis-manage
```

Or add as a dev-dependency:
```bash
uv add --group dev qgis-manage
```

Or using `pip`:
```bash
pip install qgis-manage
```

---

## 📖 Help

Every command provides a structured `--help` output with usage, options, and examples.

```text
$ qgis-manage --help

qgis-manage v0.8.0
QGIS Plugin Manager - Modern CLI for plugin development.

Usage: qgis-manage [-h] ... SUBCOMMAND ...

Subcommands:
  deploy      Deploy the plugin to the local QGIS profile
  compile     Compile resources, UI files and translations
  package     Create distributable ZIP package
  ...

General Options:
  -h, --help    show this help message and exit
  ...

Examples:
    # Initialize a new processing plugin
    qgis-manage init "My Plugin" --author "Tester" ...

Full documentation and error reports at: https://github.com/geociencio/qgis-plugin-manager
```

The full command reference is also available as static Markdown files in the [`help/`](help/) directory. Regenerate them with `make help`.

---

## 🛠️ Command Reference

### 1. Project Initialization
Scaffold a professional plugin project from a template: `default`, `processing`, or `dockwidget`.
```bash
# Create a processing plugin
qgis-manage init "My Plugin" --author "Tester" --email "test@test.com" --template processing

# Create a dockwidget plugin
qgis-manage init "My Plugin" --template dockwidget
```

### 2. Development & Deployment
Speed up your local iteration with QGIS 3 and QGIS 4 support.
```bash
# Smart deploy to default QGIS 3 profile
qgis-manage deploy

# Deploy to QGIS 4 profile
qgis-manage deploy --qgis-version 4

# Deploy to a specific profile
qgis-manage deploy --profile production

# Purge old backups to save space
qgis-manage deploy --purge-backups
```

**💡 Smart Path Detection**: `qgis-manage` automatically detects your plugins directory across Linux, macOS, and Windows. If a profile doesn't exist, it will interactively ask if you want to create it or specify a custom location.

### 3. Resource Compilation (`compile`)
Compile Qt resources, UI files, translations, and documentation.
```bash
# Compile .ui, .qrc, .ts and docs
qgis-manage compile

# Compile only translations
qgis-manage compile --type translations
```

### 4. Advanced Hooks (`hooks`)
Manage and test your native Python hooks.
```bash
# List all hooks from pyproject.toml and plugin_hooks.py
qgis-manage hooks list

# Initialize a standard plugin_hooks.py template
qgis-manage hooks init

# Test a hook in isolation without deploying
qgis-manage hooks test pre_deploy
```

### 5. Automated Versioning (`bump`)
Keep your versions in sync across all project files.
```bash
# Increment version (Patch, Minor, Major)
qgis-manage bump patch   # 0.1.0 -> 0.1.1
qgis-manage bump minor   # 0.1.1 -> 0.2.0

# Sync metadata.txt from pyproject.toml source of truth
qgis-manage bump sync
```

### 6. Packaging & Compliance
Prepare for the Official QGIS Plugin Repository.
```bash
# Create a "Repo-Ready" ZIP package
qgis-manage package

# Package with strict compliance check (fails if binaries or errors found)
qgis-manage package --repo-check --sync-version

# Stamp git build info (commit SHA, commit number, datetime, experimental)
qgis-manage package --stamp
```

### 7. Maintenance & Quality
```bash
# Run deep structural validation
qgis-manage validate --strict --repo

# Run QGIS Plugin Analyzer on the project
qgis-manage analyze

# Install plugin dependencies into a local folder
qgis-manage install-deps --target libs

# Clean caches, compiled UI/resources and docs output
qgis-manage clean

# Remove the deployed plugin from the QGIS profile
qgis-manage dclean
```

---

## ⚙️ Configuration (`pyproject.toml`)

Leverage YOUR existing configuration. No new files needed.

```toml
[tool.qgis-manager]
qgis_version = 4  # Target QGIS 4 by default
max_backups = 5   # Control backup rotation
profile = "default"

[tool.qgis-manager.ignore]
ignore = [
    "data/*.csv",
    "tests/temp/*"
]

[tool.qgis-manager.hooks]
post_deploy = "python scripts/notify.py"
```

## 🌍 Internationalization (i18n)

Automated compilation and management of `.ts` and `.qm` translation files is handled by the `compile` command (see the Command Reference above).

## 📄 License
GPL-2.0-or-later
