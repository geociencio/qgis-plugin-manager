# QGIS Plugin Manager v0.4.1

## 🧹 Cleaner Packaging & Bug Fixes

This release focuses on ensuring that generated ZIP packages are clean and free of unnecessary development files.

### 🐛 Fixes
*   **Improved Exclusion Logic**: Fixed an issue where nested directories matching wildcard patterns (like `*.egg-info` inside `src/`) were incorrectly included in the package.
*   **Expanded Ignore List**: The default exclusion list now covers a much wider range of development tools and artifacts, ensuring they don't leak into your deployments or releases.
    *   Ignored: `.vscode`, `.idea`, `uv.lock`, `poetry.lock`, `.mypy_cache`, and more.

### 📦 Installation/Upgrade

```bash
pip install qgis-plugin-manager --upgrade
# or with uv
uv add qgis-plugin-manager
```

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/compare/v0.4.0...v0.4.1
