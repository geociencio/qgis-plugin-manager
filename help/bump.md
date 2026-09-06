# qgis-manage bump

```text
qgis-manage bump v0.9.0
Automate project versioning

Usage: qgis-manage bump [-h] [path] SUBCOMMAND ...

Arguments:
  path        Project directory path (default: current directory)
  SUBCOMMAND  Bump subcommand
    major     Bump major version (X.y.z -> X+1.0.0)
    minor     Bump minor version (x.Y.z -> x.Y+1.0)
    patch     Bump patch version (x.y.Z -> x.y.Z+1)
    sync      Sync metadata.txt with pyproject.toml version

Options:
  -h, --help  show this help message and exit

Examples:
    # Bump the patch version
    qgis-manage bump patch

    # Sync metadata.txt from pyproject.toml
    qgis-manage bump sync
```

# qgis-manage bump major

```text
Usage: qgis-manage bump major [-h]

Options:
  -h, --help  show this help message and exit
```

# qgis-manage bump minor

```text
Usage: qgis-manage bump minor [-h]

Options:
  -h, --help  show this help message and exit
```

# qgis-manage bump patch

```text
Usage: qgis-manage bump patch [-h]

Options:
  -h, --help  show this help message and exit
```

# qgis-manage bump sync

```text
Usage: qgis-manage bump sync [-h]

Options:
  -h, --help  show this help message and exit
```
