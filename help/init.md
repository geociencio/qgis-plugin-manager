# qgis-manage init

```text
qgis-manage init v0.8.0
Initialize a new QGIS plugin project scaffolding

Usage: qgis-manage init [-h] [--path PATH] [--author AUTHOR] [--email EMAIL]
                        [--description DESCRIPTION] [--template TEMPLATE]
                        name

Arguments:
  name                  Name of the plugin

Options:
  -h, --help            show this help message and exit
  --path PATH           Directory where the project folder will be created
  --author AUTHOR       Author of the plugin
  --email EMAIL         Author email
  --description DESCRIPTION
                        Plugin description
  --template TEMPLATE   Project template (default, processing, dockwidget)

Examples:
    # Create a processing plugin
    qgis-manage init "My Plugin" --author "Tester" --email "test@test.com" --template processing
```
