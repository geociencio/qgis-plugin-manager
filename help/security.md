# qgis-manage security

```text
qgis-manage security v0.9.0
Run a security audit (secrets and PyQGIS rules)

Usage: qgis-manage security [-h] [--strict] [-o OUTPUT] [path]

Arguments:
  path                  Project directory path (default: current directory)

Options:
  -h, --help            show this help message and exit
  --strict              Enable strict gold-standard rules
  -o OUTPUT, --output OUTPUT
                        Output directory for reports

Examples:
    # Scan for secrets and PyQGIS security issues
    qgis-manage security

    # Scan with strict gold-standard rules
    qgis-manage security --strict
```
