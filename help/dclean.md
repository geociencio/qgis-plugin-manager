# qgis-manage dclean

```text
qgis-manage dclean v0.9.0
Remove the deployed plugin from the QGIS profile

Usage: qgis-manage dclean [-h] [-p PROFILE] [--qgis-version QGIS_VERSION]
                          [--yes]
                          [path]

Arguments:
  path                  Project directory path (default: current directory)

Options:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        QGIS profile name (default: default)
  --qgis-version QGIS_VERSION
                        Major QGIS version (3 or 4)
  --yes, -y             Remove without asking for confirmation

Examples:
    # Remove the plugin from the default QGIS profile
    qgis-manage dclean

    # Remove from a QGIS 4 profile without confirmation
    qgis-manage dclean --qgis-version 4 --yes
```
