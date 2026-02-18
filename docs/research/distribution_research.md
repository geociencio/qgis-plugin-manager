# Research: QGIS Plugin Distribution & Deployment Tools

This document analyzes standard tools in the QGIS ecosystem (`pb_tool`, `qgis-plugin-ci`) to identify features that can enhance `qgis-plugin-manager`.

## 1. Tool Analysis

### [pb_tool](https://github.com/g-sherman/pb_tool)
**Focus**: Local development workflow and packaging.

| Feature | Description | Status in qgis-manager |
| :--- | :--- | :--- |
| **Config-based** | Uses `pb_tool.cfg` to define file groups. | Uses `pyproject.toml` (Modern) |
| **Deployment** | Direct sync to QGIS profile directories. | **Implemented** (Phase 4) |
| **Quick Deploy** | Skips compilation for faster iteration. | Missing |
| **Cleanup** | `dclean` to remove deployed plugins. | **Implemented** (Phase 6) |
| **Packaging** | Generates distribution ZIP. | **Implemented** (Basic) |

### [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci)
**Focus**: Automation and CI/CD pipelines.

| Feature | Description | Status in qgis-manager |
| :--- | :--- | :--- |
| **Official Repo Upload** | Automates submission to QGIS repository. | Missing |
| **Changelog Sync** | Syncs `metadata.txt` from `CHANGELOG.md`. | Missing |
| **Transifex Sync** | Automates translation workflows. | Missing |
| **Custom Repos** | Generates `plugins.xml` for self-hosted repos. | Missing |
| **Asset Release** | Automates GitHub/GitLab releases. | Missing |

## 2. QGIS Official Repository Requirements

To be accepted, the ZIP must follow these strict rules:
1.  **Single Root Folder**: Everything must be inside one folder named after the plugin slug.
2.  **Mandatory Files**: `metadata.txt`, `__init__.py`, and `LICENSE`.
3.  **No Binaries**: Shared libraries or pre-compiled binaries are generally rejected.
4.  **Encoding**: `metadata.txt` must be UTF-8.

## 3. Recommended Improvements

Based on this research, here is the proposed roadmap for **v0.7.0+**:

### 📦 Distribution Excellence
- **[ ] Repository Validator**: Add a strict check that ensures compliance with all official QGIS repository rules.
- **[ ] Version & Changelog Sync**: Automatically update `metadata.txt` version and changelog from `pyproject.toml` or `CHANGELOG.md`.
- **[ ] Release Workflow**: A command to generate the `plugins.xml` for custom repositories.

### 🚀 Developer Velocity
- **[ ] Quick Deploy**: Option to skip resource compilation if only Python files changed.
- **[ ] Environment Scaffolding**: Support for generating GitHub Actions/GitLab CI templates.

### 🌍 Internationalization (i18n)
- **[ ] Transifex/Crowdin Integration**: Basic support for pulling/pushing `.ts` files to translation services.
