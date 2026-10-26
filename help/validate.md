# qgis-manage validate

```text
qgis-manage validate v0.15.0
Validate metadata.txt compliance and project structure

Usage: qgis-manage validate [-h] [--zip ZIP] [--strict-permissions]
                            [--max-size-mb MAX_SIZE_MB]
                            [--icon-min-px ICON_MIN_PX] [--strict] [--json]
                            [--repo]
                            [path]

Arguments:
  path                  Project directory path (default: current directory)

Options:
  -h, --help            show this help message and exit
  --zip ZIP             Validate a built ZIP artifact instead of a project
                        tree
  --strict-permissions  Treat non-portal ZIP permissions as errors
  --max-size-mb MAX_SIZE_MB
                        Maximum ZIP size in MB (default: 25)
  --icon-min-px ICON_MIN_PX
                        Minimum icon dimension in pixels (default: 32)
  --strict              Fail on warnings
  --json                Emit machine-readable JSON on stdout
  --repo                Check compliance with official QGIS repository

Examples:
    # Run deep structural validation
    qgis-manage validate --strict --repo
```
