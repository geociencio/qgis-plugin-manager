# Release Notes - v0.6.0
## "The Council of Sages: Advanced Automation"

This release marks a significant evolution in the `qgis-plugin-manager` toolset, focusing on advanced automation, developer flexibility, and improved project structuring.

### Key Highlights

#### 🛡️ Robust Exclusion Logic (`.qgisignore`)
You can now define precisely which files should be excluded from your deployments and packages using a `.qgisignore` file at the root of your project. It supports gitignore-style patterns, giving you total control over your artifacts.

#### 📦 Integrated Dependency Management
Managing third-party libraries for QGIS plugins has always been a challenge. v0.6.0 introduces `install-deps`, allowing you to define dependencies in `pyproject.toml` and install them directly into a local `libs/` folder within your plugin.

#### 🏗️ Template-Based Scaffolding
The `init` command has been completely refactored. It now uses a system of templates, allowing you to start different types of projects (standard plugins or Processing algorithms) with a single flag.

#### 🐍 Native Python Hooks
Hooks are no longer limited to shell commands. You can now execute `.py` scripts directly as hooks. The tool automatically provides the `QGIS_PROJECT_ROOT` environment variable so your scripts can easily interact with the project context.

#### 🔍 Unified Quality Analysis
The `qgis-analyzer` is now a first-class citizen. You can run full project quality checks directly via `qgis-manage analyze`.

---

### Full List of Changes

**Added:**
- Support for `.qgisignore` files.
- `qgis-manage install-deps` command.
- `--template` option for `qgis-manage init`.
- Support for `.py` hooks in `run_hook`.
- `qgis-manage analyze` command integration.

**Improved:**
- Refactored `IgnoreMatcher` for recursive and root-relative pattern matching.
- Updated project initialization to use template rendering.
- Standardized project context injection for hooks.

---
*For more details on how to use these new features, check the [Walkthrough](file:///home/jmbernales/.gemini/antigravity/brain/ac20b052-c459-4a4d-9ba5-eb9d02a43bdc/walkthrough.md).*
