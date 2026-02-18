# Competitive Analysis: The QGIS Plugin Tooling Ecosystem

This document analyzes how `qgis-plugin-manager` compares to other popular tools and what makes it the modern successor to traditional workflows.

## 1. Tool Landscape

| Tool | Core Philosophy | Config Format | Best For |
| :--- | :--- | :--- | :--- |
| **pb_tool** | The OG developer utility. | `.cfg` (INI) | Local builds & simple packaging. |
| **qgis-plugin-ci** | The CI/CD Automator. | `.yml` / `cfg` | GitHub Actions, Transifex, & Repo uploads. |
| **qgis-plugin-dev-tools** | The Env Specialist. | `pyproject.toml` | Debugging & editable installs. |
| **qgis-plugin-manager** | **The Modern Lifecycle Manager.** | **pyproject.toml** | **Production-grade dev, sync, & compliance.** |

---

## 2. Feature Comparison Matrix

| Feature | pb_tool | qgis-plugin-ci | qgis-plugin-manager |
| :--- | :--- | :--- | :--- |
| **Configuration** | Legacy Configuration | Hybrid | **Pure PEP 621 (TOML)** |
| **Deployment** | "Delete & Copy" | N/A | **Smart Sync (rsync-like)** |
| **Backups** | None | None | **Rotation & Multi-profile** |
| **Hooks** | Shell only | Shell only | **Native Python + Shell** |
| **I18n** | Basic `.ts` build | Transifex Sync | Integrated Metadata Prep |
| **Validation** | Metadata only | Schema only | **Deep Structure + Repo Compliance** |
| **Modern RCC** | Fixed tools | Limited | **Dynamic Tool Detection & Patching** |

---

## 3. What Makes the Difference? (Our USP)

### 🥇 Smart Synchronization (Sync v2.0)
While others simply delete the old plugin and copy a new one (slow and wears out SSDs), we use an **idempotent sync** logic. We only copy files that changed and remove those that no longer exist. This is critical for large plugins with many assets.

### 🥈 Native Python Hooks architecture
Traditional tools rely on `Makefiles` or shell scripts. We support `plugin_hooks.py`, allowing developers to write **Type-Safe Python code** that receives the full project context (metadata, paths, profile) during deployment and packaging.

### 🥉 Official Repository "First-Time-Right"
Our `--repo-check` and structural validation are designed to catch errors *before* you upload to QGIS. We detect prohibited binaries, malformed metadata, and incorrect license structures automatically.

### 🤖 AI-Agent Friendly
Designed from the ground up to be managed by AI (like Antigravity). The class-based command system and clear metadata make it the easiest tool for an agent to automate, as seen by our **Quality Score** integration.

## 4. Summary: When to use which?

- Use **pb_tool** if you have legacy projects with old `.cfg` files.
- Use **qgis-plugin-ci** specifically for your GitHub Actions upload step.
- Use **qgis-plugin-manager** for **everything else**: everyday development, rapid deployment, backup safety, and professional distribution prep.
