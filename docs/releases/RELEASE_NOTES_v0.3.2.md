# 🚀 QGIS Plugin Manager v0.3.2

This release fixes a bug that caused legitimate subdirectories to be excluded during deployment and packaging.

## 🛠️ Fixes

### Directory Exclusions
- **Resolved**: Fixed over-broad exclusion logic that skipped subdirectories named `tools`, `tests`, `scripts`, or `research` if they were nested inside included modules (e.g., `gui/tools`).
- **Improved**: Directory exclusion logic now distinguishes between root-level development folders and nested module subdirectories.

## 📦 Installation

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.3.2
```

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.3.1...v0.3.2
