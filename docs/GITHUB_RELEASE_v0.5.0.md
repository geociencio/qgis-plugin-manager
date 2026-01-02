# Release v0.5.0: Modernization & UI Enhancements

## What's Changed
* **Full migration to Unittest**: Removed `pytest` in favor of the standard library's `unittest` for a leaner dev environment.
* **Real-time Compilation Progress**: Added progress bar integration and async execution to the `compile` and `deploy` commands.
* **Architectural Refactoring**: Improved `compile_docs` logic to support real-time output reporting via callbacks.
* **Makefile Simplified**: `make test` now uses native discovery.

## Full Changelog
See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes.

**Dependencies removed**: `pytest`, `pytest-mock`.
