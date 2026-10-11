# Release Notes - qgis-manage v0.6.4 - improve symlink safety, cache cleaning, SemVer validation and exclusive qgisignore loading

We are pleased to announce the release of **qgis-manage v0.6.4**. This patch focuses on architectural hardening of the core, packaging, and validation subsystems, addressing edge cases identified during real-world plugin development.

## 🚀 What's Improved

### 🔗 Symlink Safety in Packaging and Discovery
`qgis-manage package` and the internal file discovery engine (`get_source_files`) now explicitly skip symbolic links, preventing infinite recursion crashes when a project contains circular or deeply nested symlinks.

### 🧹 Extended Cache Cleaning
`qgis-manage clean` now removes a wider range of development artifacts:
- `.pytest_cache` and `.ruff_cache` directories
- QGIS/Shapefile sidecar files: `*.qpj`, `*.cpg`

### 📂 Exclusive `.qgisignore` Support
If a `.qgisignore` file is present in the project root, `qgis-manage` will **no longer merge** it with `.gitignore`. The `.qgisignore` takes full precedence, allowing you to define package-specific exclusions independently of your Git configuration.

Additionally, `IgnoreMatcher` now correctly handles **implicit directory recursion**: a pattern like `logs/debug` will now match all files nested under `logs/debug/`, consistent with standard Git ignore behavior.

### ✅ Semantic Versioning 2.0 Validator
The version validator in `validation.py` was rewritten using the official [SemVer 2.0.0](https://semver.org/) specification. Pre-release identifiers such as `1.0.0-beta.1` and `1.0.0-alpha` are now valid in `metadata.txt`.

## 🐛 Bug Fixes
- Fixed `E501` (line-too-long) linting errors in `core.py` and `validation.py`.
- Updated `test_validation.py` to correctly accept pre-release version strings.

## 📦 Installation
```bash
pip install qgis-manage==0.6.4
# or
uv tool install qgis-manage@latest
```

## 📄 Full Changelog
See [CHANGELOG.md](../../CHANGELOG.md) for a complete list of changes.
