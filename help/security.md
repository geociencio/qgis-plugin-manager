# qgis-manage security

```text
qgis-manage security v0.15.0
Run a security audit (secrets and PyQGIS rules)

Usage: qgis-manage security [-h] [--strict] [-o OUTPUT] [--portal]
                            [--exclude EXCLUDE] [--json]
                            [--fail-on {critical,warning,info,none}]
                            [path]

Arguments:
  path                  Project directory path (default: current directory)

Options:
  -h, --help            show this help message and exit
  --strict              Enable strict gold-standard rules
  -o OUTPUT, --output OUTPUT
                        Output directory for reports
  --portal              Run Bandit/detect-secrets/Flake8 plus native rules
  --exclude EXCLUDE     Additional analyzer exclude pattern (repeatable)
  --json                Emit a machine-readable security report
  --fail-on {critical,warning,info,none}
                        Portal security failure threshold (default: critical)

Examples:
    # Scan for secrets and PyQGIS security issues
    qgis-manage security

    # Scan with strict gold-standard rules
    qgis-manage security --strict
```
