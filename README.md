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

## 🥇 The "Manager" Difference

`qgis-plugin-manager` is the modern successor to traditional QGIS development workflows.

### 📊 Ecosystem Comparison

| Feature | pb_tool | qgis-plugin-ci | qgis-plugin-dev-tools | qgis-plugin-manager |
| :--- | :--- | :--- | :--- | :--- |
| **Configuration** | `pb_tool.cfg` (INI) | `.qgis-plugin-ci` (YAML) or `setup.cfg`/`pyproject.toml` | `pyproject.toml` | **`pyproject.toml` (PEP 621)** |
| **Scaffolding** | `create` (templates) | — | — | `init` (templates) |
| **Local deploy** | Delete & copy | — | — | **Smart sync (rsync-like)** |
| **Backups** | None | None | None | **Rotation & multi-profile** |
| **Hooks** | None | None | None | **Native Python + Shell** |
| **Validation** | Config/environment | `metadata.txt` (schema) | — | **Deep structure & compliance** |
| **Packaging** | `zip` + version stamp | `package`/`release` | `package` | `package` + `--repo-check` |
| **Translations** | `lrelease` | **Transifex (full)** | — | `compile` (ts→qm) |
| **RCC / UI** | auto pyuic + rcc | `.qrc` only | — | **Dynamic tooling + patching** |
| **Runtime deps** | — | — | **vendoring** | `install-deps` |

Related tools in the ecosystem: **QGIS Plugin Builder** (official GUI scaffolding inside QGIS), **qgis-plugin-repo** ([3liz](https://github.com/3liz/qgis-plugin-repo), merges `plugins.xml` for custom repositories), and **qgis_devtools** ([nextgis](https://github.com/nextgis/qgis_devtools), an in-QGIS debugging plugin).

### 🚀 Key Differentiators (USPs)

- **Smart Synchronization (Sync v2.0)**: We use idempotent sync logic. Instead of slow "delete and copy", we only update modified files.
- **Native Python Hooks Architecture**: Write your automation in pure Python via `plugin_hooks.py`. Hooks receive full project context (metadata, paths, profiles).
- **Official Repository "First-Time-Right"**: Built-in `--repo-check` and structural validation catch errors *before* you upload to QGIS.
- **Automation-Friendly**: Structured `--help` output and a modular command system make it easy to script and integrate into CI pipelines.

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
  compile     Compile resources and translations
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
Scaffold a professional plugin project.
```bash
# Create a processing plugin
qgis-manage init "My Plugin" --author "Tester" --email "test@test.com" --template processing
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
Compile Qt resources, translations, and documentation.
```bash
# Compile resources, translations and docs
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
```

### 7. Maintenance & Quality
```bash
# Run deep structural validation
qgis-manage validate --strict --repo

# Run QGIS Plugin Analyzer on the project
qgis-manage analyze

# Install plugin dependencies into a local folder
qgis-manage install-deps --target libs

# Clean Python artifacts (__pycache__) and build files
qgis-manage clean
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
