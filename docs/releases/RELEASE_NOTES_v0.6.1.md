# Release v0.6.1 - The Modernization & Expansion Update 🚀

This release marks the transformation of `qgis-plugin-manager` into `qgis-manage`, a professional-grade lifecycle manager for QGIS development.

## 🌟 Highlights

### 🪝 Advanced Hooks (`hooks`)
Manage your native Python automation with ease.
- `hooks list`: Scan and discover all available hooks.
- `hooks init`: Generate a professional `plugin_hooks.py` template.
- `hooks test <name>`: Run your hooks in total isolation without full deployment.

### ⬆️ Automated Versioning (`bump`)
Keep your project versions synchronized and compliant.
- `bump major/minor/patch`: Automated Semantic Versioning.
- `bump sync`: Flawless alignment between `pyproject.toml` and `metadata.txt`.

### 🏗️ Modular Architecture
The entire CLI has been refactored for performance and extensibility. Specifically designed to be "Agent-Friendly" and 100% type-safe.

### 📋 Professional Identity
- Full suite of health badges (CI, Ruff, Mypy, Maintenance).
- Optimized PyPI metadata and hierarchical documentation.

## 🛠️ Technical Internal Changes
- **Fixed**: 10+ Mypy type safety errors.
- **Improved**: Smart Sync logic and recursive ignore matching.
- **New**: PEP 621 compliance for Tool-only projects.

---
*Developed with ❤️ by Geociencio*
