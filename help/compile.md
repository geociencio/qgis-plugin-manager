# qgis-manage compile

```text
qgis-manage compile v0.9.0
Compile resources, UI files and translations

Usage: qgis-manage compile [-h] [--type {resources,translations,docs,all}]
                           [path]

Arguments:
  path                  Project directory path (default: current directory)

Options:
  -h, --help            show this help message and exit
  --type {resources,translations,docs,all}
                        Type of resources to compile (default: all)

Examples:
    # Compile resources and translations
    qgis-manage compile

    # Compile only translations
    qgis-manage compile --type translations
```
