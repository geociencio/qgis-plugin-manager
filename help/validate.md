# qgis-manage validate

```text
qgis-manage validate v0.12.0
Validate metadata.txt compliance and project structure

Usage: qgis-manage validate [-h] [--strict] [--json] [--repo] [path]

Arguments:
  path        Project directory path (default: current directory)

Options:
  -h, --help  show this help message and exit
  --strict    Fail on warnings
  --json      Emit machine-readable JSON on stdout
  --repo      Check compliance with official QGIS repository

Examples:
    # Run deep structural validation
    qgis-manage validate --strict --repo
```
