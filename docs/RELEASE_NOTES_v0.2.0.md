# 🚀 QGIS Plugin Manager v0.2.0

A modern CLI tool for managing QGIS plugin development, deployment, and packaging.

> [!IMPORTANT]
> This is a **CLI tool**, not a QGIS plugin. Install it as a Python package using `uv` or `pip`.

## 📦 Installation

### Using uv (Recommended)

```bash
# Install as a global tool
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.2.0

# Or add to your project's dev dependencies
uv add --group dev qgis-plugin-manager @ git+https://github.com/geociencio/qgis-plugin-manager.git@v0.2.0
```

### Using pip

```bash
pip install git+https://github.com/geociencio/qgis-plugin-manager.git@v0.2.0
```

## ✨ What's New in v0.2.0

### 🎯 Key Highlights

- **📚 Comprehensive Documentation**: All Python modules now have detailed docstrings
- **⚖️ GPL v2+ License Headers**: Proper legal headers with Git SHA placeholder support
- **📊 Code Quality Badge**: Achieved 74.2/100 score from qgis-analyzer
- **🔧 Custom Profile Support**: Deploy to any QGIS profile with `--profile` flag
- **✅ Full Test Coverage**: Comprehensive unit test suite with 15 tests
- **🤖 CI/CD Pipeline**: GitHub Actions workflow for Linux, Windows, and macOS

### Added

- Feature: Support for deploying to custom QGIS profiles via `--profile` flag in `deploy` command
- Testing: Comprehensive unit test suite for core module (`tests/test_core.py`)
- CI: GitHub Actions workflow with matrix strategy (Linux, Windows, macOS / Python 3.10-3.12)
- Docs: Status badges for CI, License, and Code Style in README
- Docs: Comprehensive module-level docstrings for all Python source files
- Docs: GPL v2+ license headers in all source files with Git SHA placeholder support
- Docs: Code quality badge (74.2/100) in README
- Docs: Important clarification note in README about being a CLI tool, not a QGIS plugin
- Config: `.gitattributes` file for Git keyword expansion and consistent line endings

### Changed

- Refactor: Replaced insecure `os.system` calls with `subprocess.run` across the codebase
- Security: Improved error handling in external command execution
- Docs: Enhanced README with better project description and usage clarity

### Fixed

- Localization: Fixed hardcoded Chinese log messages in artifact cleaning

## 🛠️ Usage

```bash
# Deploy to default QGIS profile (with automatic backup)
qgis-manage deploy

# Deploy to a specific profile
qgis-manage deploy --profile production

# Compile all resources and translations
qgis-manage compile

# Clean Python artifacts
qgis-manage clean
```

## 📊 Quality Metrics

- **Code Score**: 74.2/100
- **Test Coverage**: 15/15 tests passing
- **Python Support**: 3.10, 3.11, 3.12, 3.13
- **Platforms**: Linux, macOS, Windows

## 📄 License

GPL-2.0-or-later

## 🙏 Acknowledgments

Built with modern Python tooling:
- [uv](https://github.com/astral-sh/uv) for package management
- [ruff](https://github.com/astral-sh/ruff) for linting
- [pytest](https://pytest.org) for testing
- [mypy](https://mypy-lang.org) for type checking

---

**Full Changelog**: https://github.com/geociencio/qgis-plugin-manager/blob/main/CHANGELOG.md
