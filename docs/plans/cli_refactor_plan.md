# Implementation Plan: CLI Modularization (Analyzer Architecture)

Refactor the `qgis-plugin-manager` command system to adopt the professional, modular structure used in `qgis-plugin-analyzer`. This will improve maintainability and allow for easier integration of complex commands.

## Proposed Changes

### [Component Name] CLI Layer (src/qgis_manager/cli)

#### [NEW] [base.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/base.py)
Create a base command class that standardizes how commands are defined and executed.

#### [NEW] [app.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/app.py)
Implement the `CLIApp` class to handle command discovery and registration.

#### [NEW] [commands/](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/commands/)
Modularize existing commands into separate files:
- `deploy.py`: Deployment logic.
- `compile.py`: Resource compilation.
- `package.py`: ZIP creation.
- `init.py`: Project scaffolding.
- `analyze.py`: Integration with qgis-plugin-analyzer.

#### [MODIFY] [cli.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli.py)
Transform this into a thin entry point that instantiates `CLIApp` and runs it.

## Verification Plan

### Automated Tests
- Verify that each command still works with its existing arguments.
- Check help output of the new CLI.

### Manual Verification
- Run `qgis-manage --help` to verify the new structure.
- Run `qgis-manage deploy .` to ensure parity with the previous version.
