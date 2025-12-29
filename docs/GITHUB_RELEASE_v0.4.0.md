# 🚀 QGIS Plugin Manager v0.4.0: Native Help Compilation

**v0.4.0** brings a major improvement to the development workflow by integrating native Sphinx documentation compilation directly into the tool.

## ✨ What's New in v0.4.0

### 📚 Documentation & Help
- **Native Sphinx Build**: No more external `Makefile` dependencies for help files.
- **Smart Build**: Automatically cleans Sphinx artifacts and produces a clean `help/html` folder ready for deployment.
- **CLI Type**: New `compile --type docs` command for independent build.

### 🔨 Deployment Workflow
- **Continuous Freshness**: `qgis-manage deploy` now ensures your resources and help files are re-compiled before copying to the QGIS profile.
- **Flexibility**: Use `--no-compile` to skip the automatic build during deployment.

---

## 📦 Installation

Recomendamos el uso de `uv` para la instalación como herramienta global:

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.4.0
```

o como dependencia de desarrollo en tu proyecto:

```bash
uv add --group dev qgis-plugin-manager@git+https://github.com/geociencio/qgis-plugin-manager.git@v0.4.0
```

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.3.3...v0.4.0
