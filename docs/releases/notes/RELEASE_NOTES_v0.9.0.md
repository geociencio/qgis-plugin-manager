# Release Notes - qgis-manage v0.9.0 - UI Compilation, Stamping and Templates

We are excited to announce the release of **qgis-manage v0.9.0**. This minor release adds `.ui` compilation, build metadata stamping, bundled plugin templates and a `dclean` command.

## 🚀 Key Features

### 🎨 UI Compilation
`compile` now compiles `.ui` files to Python using `pyuic` (auto-detecting `pyuic6` then `pyuic5`), and patches generated imports to the QGIS-compatible `qgis.PyQt` namespace.

```bash
qgis-manage compile
```

### 🏷️ Build Metadata Stamping
`package --stamp` injects `version`, `commitSha1`, `commitNumber`, `dateTime` and `experimental` into the packaged `metadata.txt` — without touching your source file.

```bash
qgis-manage package --repo-check --sync-version --stamp
```

### 🧩 Plugin Templates
`init` now scaffolds from bundled templates: `default`, `processing`, and `dockwidget`.

```bash
qgis-manage init "My Plugin" --template processing
```

### 🗑️ dclean
Remove the deployed plugin from a QGIS profile.

```bash
qgis-manage dclean
```

### 🔒 Security Audit
Run a focused security audit (secrets detection and PyQGIS rules) powered by `qgis-plugin-analyzer`.

```bash
qgis-manage security --strict
```

## 🛠️ Improvements

- **Cleanup**: `clean` now also removes compiled `.ui`/`.qrc` Python outputs and Sphinx `help/` output.

## 📦 Installation

```bash
uv tool install qgis-manage@latest
# or
pip install qgis-manage==0.9.0
```

## 📄 Full Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for a complete list of changes.
