# QGIS Plugin Manager

[![PyPI version](https://img.shields.io/pypi/v/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![Python versions](https://img.shields.io/pypi/pyversions/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![CI](https://github.com/geociencio/qgis-plugin-manager/actions/workflows/main.yml/badge.svg)](https://github.com/geociencio/qgis-plugin-manager/actions/workflows/main.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/geociencio/qgis-plugin-manager/graphs/commit-activity)
[![License: GPL v2+](https://img.shields.io/badge/License-GPL%20v2%2B-blue.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-79.4%2F100-brightgreen)](analysis_results/PROJECT_SUMMARY.md)
[![GitHub stars](https://img.shields.io/github/stars/geociencio/qgis-plugin-manager.svg?style=social&label=Star)](https://github.com/geociencio/qgis-plugin-manager/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/geociencio/qgis-plugin-manager.svg?style=social&label=Issue)](https://github.com/geociencio/qgis-plugin-manager/issues)

**QGIS Plugin Manager** is a professional, high-performance CLI tool designed to manage the full lifecycle of QGIS plugins. From local development and smart synchronization to official repository compliance and automated versioning. Now available on **PyPI** for easy integration.

---

## 🥇 The "Manager" Difference

`qgis-plugin-manager` is the modern successor to traditional QGIS development workflows.

### 📊 Ecosystem Comparison

| Feature | pb_tool | qgis-plugin-ci | qgis-plugin-manager |
| :--- | :--- | :--- | :--- |
| **Configuration** | Legacy `.cfg` | Hybrid `.yml` | **Pure PEP 621 (TOML)** |
| **Deployment** | Delete & Copy | N/A | **Smart Sync (rsync-like)** |
| **Backups** | None | None | **Rotation & Multi-profile** |
| **Hooks** | Shell only | Shell only | **Native Python + Shell** |
| **Validation** | Basic | Schema only | **Deep Structure & Compliance** |
| **Modern RCC** | Fixed tools | Limited | **Dynamic Tooling & Patching** |

### 🚀 Key Differentiators (USPs)

- **Smart Synchronization (Sync v2.0)**: We use idempotent sync logic. Instead of slow "delete and copy", we only update modified files.
- **Native Python Hooks Architecture**: Write your automation in pure Python via `plugin_hooks.py`. Hooks receive full project context (metadata, paths, profiles).
- **Official Repository "First-Time-Right"**: Built-in `--repo-check` and structural validation catch errors *before* you upload to QGIS.
- **AI-Agent Friendly**: Specifically designed to be easily automated by AI agents, featuring clear metadata and a modular command system.

---

## 📦 Installation

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

## 🛠️ Command Reference

### 1. Project Initialization
Scaffold a professional plugin project.
```bash
# Create a processing plugin
qgis-manage init "My Plugin" --author "Tester" --email "test@test.com" --template processing
```

### 2. Development & Deployment
Speed up your local iteration.
```bash
# Smart deploy to default QGIS profile
qgis-manage deploy

# Deploy to a specific profile with backup rotation
qgis-manage deploy --profile production --max-backups 5

# Purge old backups to save space
qgis-manage deploy --purge-backups
```

### 3. Advanced Hooks (`hooks`)
Manage and test your native Python hooks.
```bash
# List all hooks from pyproject.toml and plugin_hooks.py
qgis-manage hooks list

# Initialize a standard plugin_hooks.py template
qgis-manage hooks init

# Test a hook in isolation without deploying
qgis-manage hooks test pre_deploy
```

### 4. Automated Versioning (`bump`)
Keep your versions in sync across all project files.
```bash
# Increment version (Patch, Minor, Major)
qgis-manage bump patch   # 0.1.0 -> 0.1.1
qgis-manage bump minor   # 0.1.1 -> 0.2.0

# Sync metadata.txt from pyproject.toml source of truth
qgis-manage bump sync
```

### 5. Packaging & Compliance
Prepare for the Official QGIS Plugin Repository.
```bash
# Create a "Repo-Ready" ZIP package
qgis-manage package

# Package with strict compliance check (fails if binaries or errors found)
qgis-manage package --repo-check --sync-version
```

### 6. Maintenance & Quality
```bash
# Run deep structural validation
qgis-manage validate --strict --repo

# Run QGIS Plugin Analyzer on the project
qgis-manage analyze

# Clean Python artifacts (__pycache__) and build files
qgis-manage clean
```

---

## ⚙️ Configuration (`pyproject.toml`)

Leverage YOUR existing configuration. No new files needed.

```toml
[tool.qgis-manager]
max_backups = 5  # Control backup rotation

[tool.qgis-manager.ignore]
ignore = [
    "data/*.csv",
    "tests/temp/*"
]

[tool.qgis-manager.hooks]
post_deploy = "python scripts/notify.py"
```

## 🌍 Internationalization (i18n)

Automated compilation and management of `.ts` and `.qm` files is handled by `qgis-manage compile`.

## 📄 License
GPL-2.0-or-later
