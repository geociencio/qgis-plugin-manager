# Proposal: CLI Expansion Roadmap (v0.8.0+)

The recent modular refactor (Phase 6) and the distribution engine (Phase 7) provide a rock-solid foundation to transform `qgis-plugin-manager` into a full-lifecycle tool. Below is the proposed expansion of the CLI.

## 1. Profile Management (`profiles`)
Manage QGIS user profiles directly from the terminal.
- **`list`**: Show all detected QGIS profiles in the system.
- **`create <name>`**: Scaffold a new, clean QGIS profile for isolated testing.
- **`path <name>`**: Output the absolute path to a profile (useful for scripts).

## 2. Advanced Hooks (`hooks`)
Take the native Python hook system to the next level.
- **`list`**: View all hooks defined in `plugin_hooks.py` and `pyproject.toml`.
- **`test <name>`**: Run a specific hook with mock context to verify its logic.
- **`init`**: Generate a standard `plugin_hooks.py` with pre-filled event templates.

## 3. Automated Versioning (`bump`)
A single command to rule all versions.
- **`patch / minor / major`**: Automatically increments version in:
    1. `pyproject.toml` ([project].version)
    2. `metadata.txt` (version)
    3. `src/qgis_manager/__init__.py` (if applicable)
- **`sync`**: Ensure all version markers match the `pyproject.toml` source of truth.

## 4. Enhanced Distribution (`dist`)
Professional prep for the QGIS world.
- **`check`**: Deep scan for prohibited binaries and metadata compliance (Standalone repo-check).
- **`gen-xml`**: Generate a `plugins.xml` for self-hosted plugin repositories.
- **`bundle`**: Create a distribution ZIP with aggressive filtering (ignoring all dev/test/hidden files).

## 5. Modern I18n Workflow (`i18n`)
Streamline the translation process.
- **`extract`**: Run `pyside6-lupdate` automatically on all source files.
- **`stats`**: Show % completion for each `.ts` language found in the project.
- **`clean`**: Remove obsolete strings from translation files.

## 6. Real-time Iteration (`dev`)
Supercharge local development.
- **`watch`**: Start a long-running process that monitors file changes and runs `deploy` automatically.
- **`reload`**: (Integration) Trigger the QGIS 'Plugin Reloader' remotely after a successful deploy.

---

## 🛠️ Architectural Advantage
Because of our **Class-Based Command System**, adding any of these is as simple as:
1. Creating a new file in `src/qgis_manager/cli/commands/`.
2. Registering the new class in `CLIApp`.
3. Writing the logic using our existing `core.py` utilities.
