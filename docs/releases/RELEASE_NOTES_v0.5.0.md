# Release Notes - v0.5.0: Modernization & UI Enhancements (2026-01-02)

## 🚀 Highlights

This release focuses on **modernizing the development stack** and **enhancing user feedback**. We've successfully migrated to `unittest`, removed heavy testing dependencies, and implemented real-time compilation reporting for a smoother experience.

## 🛠️ Changes

### 🧪 Testing & CI
- **Unittest Migration**: Replaced all `pytest` markers and fixtures with standard `unittest.TestCase` methods.
- **Dependency Cleanup**: Removed `pytest` and `pytest-mock` from `pyproject.toml`.
- **Streamlined Makefile**: The `make test` command now uses `python -m unittest discover`.

### ✨ UI/UX & Refactoring
- **Real-time Progress**: Added progress bar labels that show exactly which file or document is being compiled.
- **Async Execution**: Refactored compilation logic to use non-blocking buffered output reading, allowing for smoother terminal updates.
- **Clean Architecture**: Simplified the internal callback mechanism for better extensibility.

### 📚 Documentation
- Updated `docs/uv_modernization_guide.md` to recommend `unittest` as the standard for QGIS plugin modernization.
- Added release notes and GitHub release templates for v0.5.0.

### ⚙️ Developer Experience
- Enhanced `.vscode/settings.json` for automatic `unittest` discovery.

## ⚠️ Important Note
Developers should run `uv sync` to update their local environments and remove the now-obsolete `pytest` packages.
