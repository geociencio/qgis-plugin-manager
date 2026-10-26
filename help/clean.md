# qgis-manage clean

```text
qgis-manage clean v0.15.0
Remove Python cache files and build artifacts

Usage: qgis-manage clean [-h] [--dry-run] [--keep-generated] [path]

Arguments:
  path              Project directory path (default: current directory)

Options:
  -h, --help        show this help message and exit
  --dry-run         Show what would be removed without deleting anything
  --keep-generated  Preserve .py files generated from .ui/.qrc sources

Examples:
    # Clean Python cache and build artifacts
    qgis-manage clean
```
