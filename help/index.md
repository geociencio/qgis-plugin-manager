# qgis-manage

```text
qgis-manage v0.7.0
QGIS Plugin Manager - Modern CLI for plugin development.

Usage: qgis-manage [-h] [-v] [--verbose] [--log-file LOG_FILE] SUBCOMMAND ...

Subcommands:
  SUBCOMMAND
    deploy             Deploy the plugin to the local QGIS profile
    compile            Compile resources and translations
    package            Create distributable ZIP package
    init               Initialize a new QGIS plugin project scaffolding
    clean              Remove Python cache files and build artifacts
    analyze            Run QGIS Plugin Analyzer on the project
    validate           Validate metadata.txt compliance and project structure
    install-deps       Install plugin dependencies to a local folder
    hooks              Manage and test plugin hooks
    bump               Automate project versioning

General Options:
  -h, --help           show this help message and exit
  -v, --version        show program's version number and exit
  --verbose, -V        Increase verbosity (can be used up to 3 times)
  --log-file LOG_FILE  Path to log file

Examples:
    # Initialize a new processing plugin
    qgis-manage init "My Plugin" --author "Tester" --email "test@test.com" --template processing

    # Deploy to the default QGIS profile
    qgis-manage deploy

    # Create a repo-ready ZIP package
    qgis-manage package --repo-check --sync-version

Full documentation and error reports at: https://github.com/geociencio/qgis-plugin-manager
```
