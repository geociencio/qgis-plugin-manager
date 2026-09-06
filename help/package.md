# qgis-manage package

```text
qgis-manage package v0.8.0
Create distributable ZIP package

Usage: qgis-manage package [-h] [-o OUTPUT] [--dev] [--repo-check]
                           [--sync-version]
                           [path]

Arguments:
  path                  Project directory path (default: current directory)

Options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory for ZIP
  --dev                 Include development files in package
  --repo-check          Strictly validate official repository compliance
                        before packaging
  --sync-version        Sync metadata.txt version from pyproject.toml

Examples:
    # Create a ZIP package
    qgis-manage package

    # Package with strict compliance check and version sync
    qgis-manage package --repo-check --sync-version
```
