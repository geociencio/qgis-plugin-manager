# QGIS Plugin Manager

[![PyPI version](https://img.shields.io/pypi/v/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![Python versions](https://img.shields.io/pypi/pyversions/qgis-manage.svg)](https://pypi.org/project/qgis-manage/)
[![License: GPL v2+](https://img.shields.io/badge/License-GPL%20v2%2B-blue.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-79.4%2F100-brightgreen)](analysis_results/PROJECT_SUMMARY.md)

**QGIS Plugin Manager** is a professional, high-performance CLI tool designed to manage the full lifecycle of QGIS plugins. From local development and smart synchronization to official repository compliance and automated versioning. Now available on **PyPI** for easy integration.

---

## 🥇 The "Manager" Difference

Unlike traditional tools like `pb_tool` or legacy Makefiles, `qgis-plugin-manager` is built for modern engineering workflows.

### Why choose us?
- **Smart Sync (rsync-like)**: No more "delete and copy". We only update modified files, drastically reducing deployment time and disk wear.
- **Native Python Hooks**: Write your automation in pure Python. Hooks receive a rich context (metadata, paths, profiles) for advanced workflows.
- **official Repository Compliance**: Built-in checks for prohibited binaries, mandatory files, and single-root folder structure.
- **TOML-Native**: Pure PEP 621 compliance via `pyproject.toml`. No more legacy `.cfg` files.

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
