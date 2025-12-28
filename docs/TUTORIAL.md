# Tutorial: QGIS Plugin Development Workflow

This tutorial guide you through the process of creating, developing, and packaging a QGIS plugin using `qgis-manage`.

## 1. Initialize a New Plugin

Create a new directory for your plugin and initialize it:

```bash
mkdir my-qgis-plugin
cd my-qgis-plugin
qgis-manage init "My Awesome Plugin" --author "Your Name" --email "your@email.com"
```

This will create a `my_awesome_plugin/` directory with the following structure:
- `metadata.txt`: Plugin metadata.
- `__init__.py`: Plugin entry point.
- `my_awesome_plugin.py`: Main plugin logic.
- `resources.qrc`: Qt resources definition.

## 2. Development and Deployment

While developing, you can deploy your plugin to your local QGIS profile to test it immediately:

```bash
# Deploys to the 'default' QGIS profile
qgis-manage deploy

# Or to a specific profile
qgis-manage deploy --profile production
```

## 3. Validating your Plugin

Before packaging, ensure your `metadata.txt` is compliant with QGIS repository standards:

```bash
qgis-manage validate

# Use strict mode to fail on warnings
qgis-manage validate --strict
```

## 4. Packaging for Distribution

Once you are ready to share your plugin, create a ZIP package:

```bash
qgis-manage package
```

The package will be created in the `dist/` directory, along with a SHA256 checksum file.

## 5. Cleaning up

Remove build artifacts and temporary files:

```bash
qgis-manage clean
```
