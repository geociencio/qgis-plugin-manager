# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-28

### Added
- Initial release of `qgis-plugin-manager`.
- CLI command `deploy` to automate plugin deployment to QGIS profiles with automatic backups.
- CLI command `compile` to handle `.qrc` resources and `.ts` translations.
- CLI command `clean` for workspace cleanup.
- Dynamic project root discovery based on `metadata.txt`.
- OS-specific QGIS profile path detection (Linux, macOS, Windows).
- Support for `uv` as the primary package manager.
