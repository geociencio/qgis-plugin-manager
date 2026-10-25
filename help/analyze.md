# qgis-manage analyze

```text
qgis-manage analyze v0.12.0
Run QGIS Plugin Analyzer on the project

Usage: qgis-manage analyze [-h] [--json] [--max-cc MAX_CC] [path]

Arguments:
  path             Project directory path (default: current directory)

Options:
  -h, --help       show this help message and exit
  --json           Emit machine-readable JSON on stdout
  --max-cc MAX_CC  Maximum cyclomatic complexity passed to qgis-analyzer

Examples:
    # Run the QGIS plugin analyzer
    qgis-manage analyze
```
