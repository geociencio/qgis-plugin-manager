# qgis-manage install-deps

```text
qgis-manage install-deps v0.9.0
Install plugin dependencies to a local folder

Usage: qgis-manage install-deps [-h] [--path PATH] [--target TARGET]

Options:
  -h, --help       show this help message and exit
  --path PATH      Project root directory
  --target TARGET  Target directory for libraries

Examples:
    # Install dependencies into the default 'libs' folder
    qgis-manage install-deps

    # Install into a custom target folder
    qgis-manage install-deps --target vendor
```
