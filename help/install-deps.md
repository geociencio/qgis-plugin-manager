# qgis-manage install-deps

```text
qgis-manage install-deps v0.10.0
Install plugin dependencies to a local folder

Usage: qgis-manage install-deps [-h] [--path PATH] [--target TARGET]
                                [--timeout TIMEOUT] [--dry-run]

Options:
  -h, --help         show this help message and exit
  --path PATH        Project root directory
  --target TARGET    Target directory for libraries
  --timeout TIMEOUT  Maximum seconds for the dependency installer
  --dry-run          Print the installer command without running it

Examples:
    # Install dependencies into the default 'libs' folder
    qgis-manage install-deps

    # Install into a custom target folder
    qgis-manage install-deps --target vendor
```
