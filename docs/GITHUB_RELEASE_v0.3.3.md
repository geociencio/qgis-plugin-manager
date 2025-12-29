# 🚀 QGIS Plugin Manager v0.3.3: Robust Hook Testing

**v0.3.3** addresses a specific test failure on Windows environments, ensuring CI reliability across all platforms.

## ✨ What's New in v0.3.3

### 🛠️ Continuous Integration
- **Fixed**: Resolved a quoting issue in `test_run_hook_success` that caused failures on Windows runners.
- **Improved**: Standardized hook verification in tests using cross-platform Python commands.

---

## 📦 Installation

Recomendamos el uso de `uv` para la instalación como herramienta global:

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.3.3
```

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.3.2...v0.3.3
