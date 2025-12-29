# 🚀 QGIS Plugin Manager v0.3.2: Improved Deployment Logic

**v0.3.2** is a maintenance release that refines how the tool handles directory exclusions, ensuring that complex plugin structures are preserved correctly during deployment and packaging.

> [!IMPORTANT]
> This is a **CLI tool**, not a QGIS plugin. Install it as a Python package using `uv` or `pip`.

## ✨ What's New in v0.3.2

### 🛠️ Deployment & Packaging
- **Fixed**: Resolved an issue where nested directories named `tools` (like `gui/tools`) were incorrectly skipped by the `deploy` and `package` commands.
- **Improved**: The exclusion logic for development folders (`tests/`, `tools/`, `scripts/`, `research/`) is now applied only at the project root level, preventing false positives in deeper directory structures.

---

## 📦 Installation

Recomendamos el uso de `uv` para la instalación como herramienta global:

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.3.2
```

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.3.1...v0.3.2
