# Release Notes - qgis-manage v0.7.0 - QGIS 4 Support and Multi-Version Deployment

We are excited to announce the release of **qgis-manage v0.7.0**. This minor release introduces full compatibility with **QGIS 4**, dynamic path detection for multiple QGIS versions, and an improved interactive deployment workflow.

## 🚀 Key Features

### 🌍 Full QGIS 4 Support
`qgis-manage` now supports deploying plugins to both QGIS 3 and QGIS 4 profiles. The core path detection engine has been updated to handle the new directory structures across Linux, macOS, and Windows.

### 🚩 New `--qgis-version` Flag
The `deploy` command now includes a `--qgis-version` (or `-v`) option to target specific QGIS major versions.
```bash
# Deploy to QGIS 4 profile
qgis-manage deploy --qgis-version 4

# Deploy to QGIS 3 (default)
qgis-manage deploy --qgis-version 3
```

### 🤖 Interactive Profile Validation
If the target QGIS profile or plugins directory does not exist, `qgis-manage` now behaves more intelligently:
- It warns you about the missing path.
- It asks if you want to create the directory automatically.
- It allows you to provide a custom absolute path manually if the detected one is not correct for your environment.

### ⚙️ Persistent Version Configuration
You can now set your preferred QGIS version globally or per-project in your `pyproject.toml`:
```toml
[tool.qgis-manager]
qgis_version = 4
profile = "default"
```

## 🛠️ Internal Improvements
- **Refactored `get_qgis_plugin_dir`**: Decoupled version detection from OS detection.
- **Enhanced Settings Schema**: Added `qgis_version` to the internal configuration model.
- **Updated Test Suite**: Comprehensive tests now validate path generation for both QGIS 3 and QGIS 4 across all supported operating systems.

## 📦 Installation
```bash
uv tool install qgis-manage@latest
# or
pip install qgis-manage==0.7.0
```

## 📄 Full Changelog
See [CHANGELOG.md](../../CHANGELOG.md) for a complete list of changes.
