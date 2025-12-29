# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-28

### Added
- **Plugin Scaffolding**: New `init` command to create a standardized QGIS plugin structure.
- **Persistent Configuration**:
  - Support for global defaults in `~/.config/qgis-manager/config.toml`.
  - Project-level overrides in `pyproject.toml` via `[tool.qgis-manager]` section.
- **Customizable Hooks**:
  - Implementation of `pre-deploy` and `post-deploy` shell hooks.
  - Configurable via `pyproject.toml`.
- **Enhanced UX/UI**:
  - Interactive mode (`--interactive`) for step-by-step deployment confirmation.
  - Progress bars (`click.progressbar`) for deployment and packaging operations.
  - Standardized colorized output and emoji feedback for improved terminal readability.
  - Intelligent "💡 Hint" suggestions for common error scenarios.
- **Advanced Logging**:
  - Global verbosity control (`-v`, `-vv`) for detailed debug information.
  - Support for logging to persistent files via `--log-file`.
- **Packaging & Validation**:
  - `package` command to create distributable ZIP files with SHA256 checksums.
  - `validate` command for strict `metadata.txt` compliance checking.
- **Documentation**:
  - New `CONTRIBUTING.md` guide for developers.
  - Comprehensive `TUTORIAL.md` for end-users.
- **Testing**:
  - Expanded test suite to 40 unit tests with 100% pass rate.
  - New dedicated test modules for config and hooks.

### Changed
- **Code Quality**: Full adoption of `Ruff` and `Mypy` for static analysis and type checking.
- **CLI Design**: Standardized error handling using `click.Abort` for consistent return codes.
- **Refactor**: Improved `core.py` architecture to support progress callbacks and hook execution.

### Fixed
- Fixed crash in `deploy` command when using progress bar (generator len error).
- Fixed redundant file copy operation in `deploy_plugin`.
- Resolved multiple linting and type hint warnings across the codebase.

## [0.2.0] - 2025-12-28

### Added
- Feature: Support for deploying to custom QGIS profiles via `--profile` flag in `deploy` command.
- Testing: Comprehensive unit test suite for core module (`tests/test_core.py`).
- CI: GitHub Actions workflow with matrix strategy (Linux, Windows, macOS / Python 3.10-3.12).
- Docs: Status badges for CI, License, and Code Style in README.
- Docs: Comprehensive module-level docstrings for all Python source files.
- Docs: GPL v2+ license headers in all source files with Git SHA placeholder support.
- Docs: Code quality badge (74.2/100) in README.
- Docs: Important clarification note in README about being a CLI tool, not a QGIS plugin.
- Config: `.gitattributes` file for Git keyword expansion and consistent line endings.

### Changed
- Refactor: Replaced insecure `os.system` calls with `subprocess.run` across the codebase.
- Security: Improved error handling in external command execution.
- Docs: Enhanced README with better project description and usage clarity.

### Fixed
- Localization: Fixed hardcoded Chinese log messages in artifact cleaning.

## [0.1.0] - 2025-12-28

### Added
- Initial release of `qgis-plugin-manager`.
- CLI command `deploy` to automate plugin deployment to QGIS profiles with automatic backups.
- CLI command `compile` to handle `.qrc` resources and `.ts` translations.
- CLI command `clean` for workspace cleanup.
- Dynamic project root discovery based on `metadata.txt`.
- OS-specific QGIS profile path detection (Linux, macOS, Windows).
- Support for `uv` as the primary package manager.
