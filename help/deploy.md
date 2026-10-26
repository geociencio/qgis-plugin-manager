# qgis-manage deploy

```text
qgis-manage deploy v0.13.0
Deploy the plugin to the local QGIS profile

Usage: qgis-manage deploy [-h] [-p PROFILE] [--no-backup] [-i] [--no-compile]
                          [--no-manifest] [--dry-run] [--purge-backups]
                          [--yes] [--qgis-version QGIS_VERSION] [--trust]
                          [path]

Arguments:
  path                  Project directory path (default: current directory)

Options:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        QGIS profile name or absolute plugins directory
                        (default: configured profile, else 'default')
  --no-backup           Skip backup of existing installation
  -i, --interactive     Ask for confirmation before each step
  --no-compile          Skip automatic resource compilation
  --no-manifest         Disable the content manifest and re-hash every file
  --dry-run             Show what would be copied, deleted, backed up or
                        purged
  --purge-backups       Remove all existing backups for this plugin
  --yes                 Assume yes for purge/create/deploy confirmations
  --qgis-version QGIS_VERSION
                        Major QGIS version (3 or 4)
  --trust               Allow hooks from this project to execute (trusted
                        checkout only)

Examples:
    # Deploy to the default QGIS profile
    qgis-manage deploy

    # Deploy to a QGIS 4 profile
    qgis-manage deploy --qgis-version 4

    # Deploy without creating a backup
    qgis-manage deploy --no-backup
```
