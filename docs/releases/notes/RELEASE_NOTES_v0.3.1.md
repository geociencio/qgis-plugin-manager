# 🚀 QGIS Plugin Manager v0.3.1

This is a patch release that fixes a critical crash discovered shortly after the v0.3.0 release.

## 🛠️ Fixes

### Deployment Crash
- **Resolved**: Fixed `TypeError: object of type 'generator' has no len()` when running the `deploy` command with the progress bar active.
- **Improved**: Added a regression test to ensure file discovery logic remains compatible with progress reporting callbacks.

## 📦 Installation

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.3.1
```

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.3.0...v0.3.1
