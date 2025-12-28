import click
from pathlib import Path
import logging
from .core import deploy_plugin, compile_qt_resources, clean_artifacts
from .discovery import find_project_root

@click.group()
def main():
    """Modern CLI for QGIS plugin development."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

@main.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--no-backup", is_flag=True, help="Skip backup of existing installation.")
def deploy(path, no_backup):
    """Deploy the plugin to the local QGIS profile."""
    try:
        root = find_project_root(path)
        deploy_plugin(root, no_backup=no_backup)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

@main.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--type", "res_type", type=click.Choice(["resources", "translations", "all"]), default="all")
def compile(path, res_type):
    """Compile resources and translations."""
    try:
        root = find_project_root(path)
        compile_qt_resources(root, res_type)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

@main.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def clean(path):
    """Clean build artifacts."""
    try:
        root = find_project_root(path)
        clean_artifacts(root)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

if __name__ == "__main__":
    main()
