# qgis-manage compile

```text
qgis-manage compile v0.15.0
Compile resources, UI files and translations

Usage: qgis-manage compile [-h] [--jobs JOBS]
                           [--type {resources,translations,docs,all}]
                           [path]

Arguments:
  path                  Project directory path (default: current directory)

Options:
  -h, --help            show this help message and exit
  --jobs JOBS           Number of files to compile concurrently (default: 1)
  --type {resources,translations,docs,all}
                        Type of resources to compile; may be repeated
                        (default: all)

Examples:
    # Compile resources and translations
    qgis-manage compile

    # Compile only translations
    qgis-manage compile --type translations
```
