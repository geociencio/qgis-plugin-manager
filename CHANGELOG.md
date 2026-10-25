# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.0] - 2026-10-25

### Added
- **JSON output**: `--json` for `validate`, `analyze` and `package`, with a versioned schema on stdout and unchanged exit codes.
- **Ignore inspection**: `ignore check <path>` and `--explain` report the winning nested/negated rule.
- **Deploy dry-run**: `deploy --dry-run` reports copy/delete/backup/purge/hook actions without mutating the target.
- **Profiles list**: `profiles list` shows profiles and plugin counts without creating anything.
- **Docs gate**: `package --require-docs` fails when `help/html/index.html` is missing.
- **Complexity passthrough**: `analyze --max-cc N` forwards the threshold to qgis-analyzer.

### Changed
- **Breaking: hooks are non-shell by default**. `HookPolicy.shell` defaults to `False`; shell syntax now requires an explicit `HookPolicy(shell=True)` and a clear migration error is logged.

## [0.11.0] - 2026-10-25

### Added
- **Deploy manifest**: cache source/target content fingerprints in `.qgis-manage/deploy-manifest.json` to skip hashing unchanged files; `--no-manifest` provides a full-scan escape hatch.
- **Reflink backups**: prefer `cp --reflink=auto` on Linux, with a safe `copytree` fallback.
- **Compile freshness**: skip translations whose `.qm` is newer than `.ts`; compile UI/QRC to a temporary output and replace only when bytes change.

### Performance
- **Repository scan**: `--repo-check` now walks once and prunes ignored/symlinked directories before looking for prohibited binaries.
- **Incremental deploy**: manifest-based checks avoid repeated content reads while preserving same-size rewrite detection.
- **Compile writes**: identical generated UI/resource output no longer rewrites files or dirties the worktree.

## [0.10.1] - 2026-10-25

### Fixed
- **Deploy backups**: use microsecond timestamps and collision-safe suffixes so consecutive deploys no longer fail with `File exists`.
- **Compile types**: make `--type` repeatable; `--type resources --type translations` now compiles both families instead of silently keeping only the last one.
- **Package versions**: reject `--release-version` when it differs from `metadata.txt` and neither `--stamp` nor a matching sync resolves it, preventing ZIP names from diverging from portal-validated metadata.
- **Non-interactive deploy**: add `deploy --yes` for purge/create/deploy confirmations; reject combining it with `--interactive`.
- **Clean safety**: add `clean --dry-run` and `clean --keep-generated`, and warn when a generated `.py` is tracked by Git.

## [0.10.0] - 2026-10-25

### Added
- **Safe lifecycle operations**: plugin names produce validated ASCII slugs; empty or unsafe names are rejected before deploy/dclean/init/package.
- **Compilation failures**: `compile` and automatic deploy compilation now exit non-zero and preserve previous documentation on failure.
- **Repository validation**: official-repository checks now require `about`/`repository`, inspect the final packaged file set and ignore dev directories.

### Fixed
- **Metadata preservation**: `bump`, `sync` and build stamping no longer destroy comments, custom sections or multiline values in `metadata.txt`.
- **Backups**: `deploy --purge-backups` now removes all matching backups instead of being a no-op, and honors an absolute `--profile` plugins directory.
- **Scaffolding**: generated class/module names are valid Python identifiers; template metadata uses a valid `0.1.0` version.
- **UI compilation**: `pyuic6`/PyQt6 imports are patched to `qgis.PyQt`.
- **Configuration**: the configured `profile` is honored and CLI flags still override it.
- **Validation**: valid `True`/`False` values no longer warn; plugin versions require `X.Y.Z`.

### Security
- **Trusted execution**: `deploy` skips project hooks and `package` refuses to install declared dependencies unless `--trust` is passed.
- **Path confinement**: deploy/package skip source symlinks and refuse symlink destinations; ZIP member names always use POSIX `/`.
- **Package versions**: path separators, empty versions and `..` are rejected before writing the ZIP.

### Changed
- **Packaging**: dependencies are installed before the compliance check and install failures abort the package.
- **Typing and tooling**: the package now ships `py.typed` and passes `mypy --strict`; `make test` uses pytest, `make lint` runs strict mypy on `src`, and `make format` applies Ruff formatting.
- **Cleanup and docs**: removed the shadowed `cli.py` and dead `IgnoreMatcher.get_ignore_func`, fixed `get_source_files(include_dev=...)`, corrected the README ignore snippet, and marked the QGIS 3 hardcode note as resolved.
- **Framework docs**: documented `// turbo` as an opencode-only runtime hint and `qa-docker` as a deprecated upstream alias not adopted by this project.
- **Release notes**: active notes now use `vX.Y.Z.md`; the release workflow falls back to legacy `RELEASE_NOTES_*.md` names and a generic body for old tags.
- **Architecture**: added `docs/architecture/AGENTIC_SYSTEM_PLANS.md` to record the Gen 7/8 plan status without modifying the shared framework submodule.
- **Internal optimization**: CLI commands are instantiated once, command errors are centralized, deploy/package orchestration is split, compile tools have timeouts and skip dev/vendor directories, and dead validation code was removed.
- **Internal architecture**: validation and metadata are modular, CLI commands use a registry, compile tools share a bounded context, and deploy detects content changes beyond size/mtime.
- **Quality hardening**: narrowed exception handling, enforced 90 % branch coverage, portable config paths, ignore negation, Git-boundary project discovery and split test suites.
- **Platform controls**: nested ignore files, policy-bounded hooks/dependencies, `compile --jobs`, and external `qgis_manager.commands` entry points.

## [0.9.2] - 2026-10-10

### Fixed
- **CI**: made the project discovery and hooks tests cross-platform so the suite passes on macOS and Windows (resolved path comparisons and UTF-8 file reads). No runtime changes.

## [0.9.1] - 2026-10-10

### Changed
- **Maintainability**: split the 840-line `core.py` into a cohesive `qgis_manager.core` package and lowered cyclomatic complexity; behaviour is unchanged.
- **Release process**: added an automated GitHub/PyPI release pipeline (`.github/workflows/release.yml`) and an 80% coverage gate in CI.

### Improved
- **Documentation**: reorganized release docs under `docs/releases/` (`notes/`, `github/`) and synced `docs/CHANGELOG.md` with the canonical changelog.
- **Agent tooling**: adopted the `agentic-forge` framework (`.agent/` submodule, project state in `.agent-state/`).

## [0.9.0] - 2026-09-06

### Added
- **UI compilation**: `compile` now compiles `.ui` files via `pyuic` (auto-detects `pyuic6`/`pyuic5`) and patches imports to `qgis.PyQt`.
- **Build metadata stamping**: `package --stamp` injects `version`, `commitSha1`, `commitNumber`, `dateTime` and `experimental` into the packaged `metadata.txt` without modifying the source. `--release-version` overrides the version.
- **Plugin templates**: `init` now scaffolds from bundled templates (`default`, `processing`, `dockwidget`) via a minimal stdlib `{{ var }}` renderer.
- **`dclean` command**: remove the deployed plugin from a QGIS profile.
- **`security` command**: run a focused security audit (secrets and PyQGIS rules) via `qgis-plugin-analyzer` (`qgis-analyzer security --deep`).

### Changed
- **Cleanup**: `clean` now also removes compiled `.ui`/`.qrc` Python outputs and Sphinx `help/` output.

## [0.8.0] - 2026-09-06

### Added
- **Structured help**: Adopted a structured `--help` template (title, usage, subcommands, examples) for the main command and every subcommand.
- **CLI reference docs**: Generated the full command reference into `help/` (Markdown) with a `make help` target.
- **Structure validation**: `package --repo-check` now also runs `validate_project_structure`.
- **pytest**: Added `pytest` to dev dependencies and configured `[tool.pytest.ini_options]`.

### Changed
- **Python 3.11+**: Raised `requires-python` to `>=3.11` and replaced `tomli` fallbacks with stdlib `tomllib`.
- **Centralized TOML handling**: Added `toml_utils.py` with `load_toml`, `get_project_version` and `set_project_version`, replacing fragile regex version editing.
- **Version sync**: Added `sync_metadata_version` in `discovery.py`, reused by `bump` and `package`.
- **Progress bars**: Extracted the duplicated compile progressbar callback into `cli/progress.py`.
- **RCC detection**: `get_rcc_tool` now uses `shutil.which` instead of running `--version`.
- **Hooks convention**: Unified hook names to underscore (`pre_deploy`/`post_deploy`).

### Fixed
- **Custom deploy path**: `deploy` now respects the interactive/manual target directory instead of ignoring it.
- **Hooks CLI**: `hooks test <hook_name>` now parses correctly via `--path` option.

### Removed
- Dead code: unreachable `return`, redundant exception clause, misleading `load_config` docstring.
- AI/agent development artifacts from the repository root.

## [0.7.0] - 2026-05-12

### Added
- **QGIS 4 Support**: Implemented full compatibility for deploying plugins to QGIS 4 profiles across all platforms (Linux, macOS, Windows).
- **Multi-Version Path Detection**: Updated `get_qgis_plugin_dir` to dynamically resolve paths based on the major QGIS version.
- **Interactive Deployment**: The `deploy` command now validates profile existence interactively, allowing users to create missing directories or specify custom paths manually.
- **CLI Flag `--qgis-version`**: New option in the `deploy` command to target specific QGIS versions (defaults to 3).
- **Enhanced Configuration**: Added `qgis_version` to `tool.qgis-manager` in `pyproject.toml` for persistent version targeting.

### Changed
- **Core Architecture**: Refactored `deploy_plugin` to propagate version settings through the deployment lifecycle.
- **Settings Model**: Integrated `qgis_version` into the standard `Settings` dataclass.

### Improved
- **Test Coverage**: Added cross-platform unit tests for QGIS 4 path detection.
- **Documentation**: Updated `README.md` and added detailed release notes for v0.7.0.

## [0.6.4] - 2026-02-19

### Improved
- **Architectural Resilience**: Improved `create_plugin_package` and `get_source_files` in `core.py` and `discovery.py` to correctly ignore `is_symlink()`, preventing infinite recursion bugs.
- **Robust Cache Cleaning**: Expanded `clean_artifacts` to purge `.pytest_cache`, `.ruff_cache`, and QGIS specific files (`*.qpj`, `*.cpg`).
- **Ignore Parser Compatibility**: `load_ignore_patterns` now treats `.qgisignore` exclusively, overriding `.gitignore` completely. Modified `IgnoreMatcher` to support implicit directory recursion semantics, identically to Git logic.
- **Official QGIS Validation**: The version validator was rewritten from a simple regex to full Semantic Versioning 2.0.0 support, enabling prereleases validation (e.g. `1.0.0-beta`).

## [0.6.3] - 2026-02-18

### Fixed
- **Structural Validation Tests**: Fixed `test_validation_deep.py` tests that failed because `__init__.py` was created empty (without `classFactory`), not satisfying the stricter validation rules introduced in v0.6.2.
- **Linting Errors**: Resolved `E501` line-too-long errors in `core.py` (`verify_resource_patch`) and `validation.py` (boolean field warning message).
- **Blank-Line Whitespace**: Removed trailing whitespace from blank lines inside `patch_resource_file` in `core.py`.

### Added
- **CI Verification Step**: Added `uv run qgis-manage --version` step to GitHub Actions workflow to verify CLI installation on every CI run.
- **Release Notes**: Added `docs/releases/notes/v0.6.3.md` with detailed release notes.
- **Maintenance Report**: Added `docs/maintenance/infrastructure_upgrade_20260218.md` documenting the validation hardening work.

## [0.6.2] - 2026-02-18

### Added
- **Advanced Hooks System**: New `hooks` command to manage native Python hooks. Features `hooks list`, `hooks init` (template generation), and `hooks test` (isolated execution with mock context).
- **Automated Versioning**: New `bump` command supporting Semantic Versioning (`major`, `minor`, `patch`) with automatic file synchronization (`bump sync`).
- **Professional Metadata**: Expanded project classifiers (GIS, CLI, Spanish) and status badges (CI, Ruff, MyPy, Maintenance) in `README.md`.
- **Tool-only Project Support**: `qgis-manage` now supports Python projects without `metadata.txt` by using `pyproject.toml` as a root marker.

### Improved
- **Modular CLI Architecture**: Refactored the entire command system into a high-performance, class-based architecture for better extensibility and AI-agent compatibility.
- **Hierarchical Documentation**: Completely reorganized `docs/` into specialized subdirectories (`research`, `plans`, `walkthroughs`, `releases`).
- **RCC Modernization**: Improved dynamic tool detection and automatic relative import patching for compiled resources.
- **Structural Validation Deepening**: Enhanced the `validate` command with strict official repository compliance checks.

### Fixed
- **Resilient Metadata Parsing**: Fixed `ConfigParser` issue that lowercased CamelCase keys and crashed on `%` symbol in `metadata.txt`.
- **Robust Persistence**: Improved `bump` synchronization and `save_plugin_metadata` resilience.
- **Type Safety**: Resolved 10+ Mypy type safety errors across the core codebase.
- **Import Resolution**: Fixed relative import issues and cleaned up redundant imports.
- **Ignore Logic**: Fixed recursive exclusion bugs in complex directory structures.

## [0.6.0] - 2026-01-02

### Added
- **.qgisignore support**: Implemented gitignore-style exclusion logic for better control over deployment and packaging.
- **Dependency Management**: New `install-deps` command to install third-party libraries into a local `libs/` folder within the plugin.
- **Enhanced Scaffolding**: Refactored `init` to use a template-based system, supporting multiple types of plugins (default, processing).
- **Python Native Hooks**: Support for executing `.py` files as hooks with automatic project context (`QGIS_PROJECT_ROOT`).
- **Unified Analyzer Command**: Integrated `qgis-analyzer` directly as `qgis-manage analyze`.

### Improved
- **Exclusion Logic**: Replaced hardcoded sets with a robust `IgnoreMatcher` class.
- **Scaffolding Automation**: Better prompt interaction for `init` command.

## [0.5.0] - 2026-01-01

### Added
- **Test Framework Migration**: Fully migrated the test suite from `pytest` to Python's standard `unittest` library.
- **Dependency Optimization**: Removed `pytest` and `pytest-mock` from development dependencies.
- **Modernized Documentation**: Updated the modernization guide and release notes.

### Improved (UI/UX & Refactoring)
- **Real-time Compilation Feedback**: Added progress bar integration for documentation and resource compilation.
- **Architectural Refactoring**:
  - `compile_docs` now uses `subprocess.Popen` for real-time output reporting via callbacks.
  - Centralized compilation callbacks to provide better terminal feedback during long operations.
- **IDE Integration**: Reconfigured `.vscode/settings.json` for `unittest`.

### Changed
- **Build System**: Updated `Makefile` to use `python -m unittest discover tests`.

## [0.4.1] - 2025-12-31

### Fixed
- **Packaging Logic**: Fixed a bug where nested directories matching wildcard exclusion patterns (e.g., `src/my_lib.egg-info`) were not being excluded from the package.
- **Improved Exclusions**: Centralized and expanded the default list of excluded files to prevent development artifacts from leaking into production packages. Now consistently ignores:
  - IDE files (`.vscode`, `.idea`, `.settings`)
  - Dependency lock files (`uv.lock`, `poetry.lock`, `Pipfile`, `Pipfile.lock`)
  - Testing and linting caches (`.mypy_cache`, `.pre-commit-config.yaml`, `.ruff_cache`)
  - Internal artifacts (`.agent`, `.ai-context`, `analysis_results`)

## [0.4.0] - 2025-12-28

### Added
- **Native Help Compilation**:
  - Integrated native Sphinx documentation compilation as a built-in feature.
  - Automatically detects `docs/source/conf.py` and compiles to `help/html`.
  - Supports `uv run sphinx-build` for consistent environment execution.
  - New `--type docs` option for the `compile` command.
- **Enhanced Deployment Workflow**:
  - `deploy` command now performs automatic compilation of resources, translations, and documentation before deployment (configurable via `auto_compile` setting).
  - New `--no-compile` flag for `deploy` command to bypass automatic compilation when needed.

### Improved
- **Testing**: Added unit tests for `compile_docs` and CLI `compile --type docs` integration, bringing total test count to 45 passing tests.

## [0.3.3] - 2025-12-28

### Fixed
- Improved recursive exclusion logic for `tools`, `tests`, `research`, and `scripts` directories to prevent accidental exclusion of nested project files (e.g., `gui/tools`).

## [0.3.2] - 2025-12-28

### Fixed
- Fixed deployment exclusion logic to ensure development-only directories are only ignored at the first level of the project path.

## [0.3.1] - 2025-12-28

### Fixed
- Fixed crash in `deploy` command when using progress bar (generator len error).

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
