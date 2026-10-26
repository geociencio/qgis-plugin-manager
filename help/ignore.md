# qgis-manage ignore

```text
qgis-manage ignore v0.15.0
Check ignore rules for a path

Usage: qgis-manage ignore [-h] [--project PATH] ACTION ...

Arguments:
  ACTION
    check         Check one path

Options:
  -h, --help      show this help message and exit
  --project PATH  Project root (default: current directory)

Examples:
    # Check a path against project ignore rules
    qgis-manage ignore check tests/tmp.txt

    # Show the rule that wins
    qgis-manage ignore check tests/tmp.txt --explain
```

# qgis-manage ignore check

```text
Usage: qgis-manage ignore check [-h] [--explain] target

Arguments:
  target      Path relative to the project root

Options:
  -h, --help  show this help message and exit
  --explain   Print the winning ignore rule
```
