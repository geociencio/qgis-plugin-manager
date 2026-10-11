# 🚀 QGIS Plugin Manager v0.3.3

This version fixes a cross-platform test failure on Windows.

## 🛠️ Fixes

### Tests
- **Resolved**: Fixed `test_run_hook_success` failure on Windows by using a more robust cross-platform command.
- **Improved**: Hook tests now use Python one-liners to avoid shell-specific quoting issues between POSIX and Windows.

## 📦 Installation

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.3.3
```

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.3.2...v0.3.3
