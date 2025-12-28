# QGIS Plugin Manager

A professional CLI for managing QGIS plugin development, deployment, and packaging. Modernized for Python 3.10+ and `uv`.

## 🚀 Features

- **Dynamic Deployment**: Automatically detects your QGIS profile directory (Linux, Windows, macOS).
- **Smart Discovery**: Reads `metadata.txt` to identify your plugin and automatically selects source files.
- **Safety First**: Automatically creates timestamped backups of your plugin folder before every deployment.
- **Qt Integration**: Compiles `.qrc` resources and `.ts` translations with simple commands.
- **Clean Workflow**: Removes `__pycache__` and artifacts recursively.

## 📦 Installation

Install system-wide as a tool using `uv`:

```bash
uv tool install git+https://github.com/geociencio/qgis-plugin-manager.git
```

Or add it to your project's development dependencies:

```bash
uv add --group dev qgis-plugin-manager @ git+https://github.com/geociencio/qgis-plugin-manager.git
```

## 🛠️ Usage

From your plugin project root:

```bash
# Deploy to QGIS profile (with automatic backup)
qgis-manage deploy

# Compile all resources and translations
qgis-manage compile

# Clean Python artifacts
qgis-manage clean
```

## 📖 Documentation

- [CHANGELOG.md](CHANGELOG.md): History of changes and releases.
- [RULES.md](RULES.md): Coding standards and project rules.

## 📄 License

GPL-2.0-or-later
