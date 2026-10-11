# 🚀 QGIS Plugin Manager v0.4.0

This version introduces native Sphinx documentation compilation and enhances the deployment workflow.

## ✨ Features

### Documentation
- **Native Help Compilation**: Integrated native Sphinx documentation compilation.
- **Automatic Detection**: Detects `docs/source/conf.py` and compiles to `help/html`.
- **Environment Support**: Automatically uses `uv run sphinx-build` if available.

### Deployment
- **Auto-Compilation**: The `deploy` command now automatically compiles resources, translations, and documentation.
- **Improved Control**: Added `--no-compile` flag to the `deploy` command.

## 📦 Installation

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.4.0
```

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.3.3...v0.4.0
