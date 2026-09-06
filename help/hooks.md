# qgis-manage hooks

```text
qgis-manage hooks v0.8.0
Manage and test plugin hooks

Usage: qgis-manage hooks [-h] [--path PATH] SUBCOMMAND ...

Arguments:
  SUBCOMMAND   Hooks subcommand
    list       List all defined hooks
    init       Initialize a plugin_hooks.py template
    test       Test a specific hook in isolation

Options:
  -h, --help   show this help message and exit
  --path PATH  Project directory path (default: current directory)

Examples:
    # List all defined hooks
    qgis-manage hooks list

    # Test the pre_deploy hook in isolation
    qgis-manage hooks test pre_deploy
```

# qgis-manage hooks list

```text
Usage: qgis-manage hooks list [-h]

Options:
  -h, --help  show this help message and exit
```

# qgis-manage hooks init

```text
Usage: qgis-manage hooks init [-h]

Options:
  -h, --help  show this help message and exit
```

# qgis-manage hooks test

```text
Usage: qgis-manage hooks test [-h] hook_name

Arguments:
  hook_name   Name of the hook to test (e.g., pre_deploy)

Options:
  -h, --help  show this help message and exit
```
