# /***************************************************************************
#  QGIS Plugin Manager
#                                  A CLI Tool
#  Modern command-line interface for QGIS plugin development and deployment.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
Command-line interface for QGIS plugin management.

This module provides Click-based CLI commands for deploying plugins to QGIS,
compiling Qt resources and translations, and cleaning build artifacts.

Commands:
    deploy: Deploy plugin to local QGIS profile with automatic backup
    compile: Compile Qt resources (.qrc) and translations (.ts)
    clean: Remove Python cache files and build artifacts
"""

import logging
from pathlib import Path

import click

from .core import clean_artifacts, compile_qt_resources, deploy_plugin
from .discovery import find_project_root


@click.group()
def main():
    """Modern CLI for QGIS plugin development."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

@main.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--no-backup", is_flag=True, help="Skip backup of existing installation."
)
@click.option(
    "-p", "--profile", default="default", help="QGIS profile to deploy to."
)
def deploy(path, no_backup, profile):
    """Deploy the plugin to the local QGIS profile."""
    try:
        root = find_project_root(path)
        deploy_plugin(root, no_backup=no_backup, profile=profile)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

@main.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--type",
    "res_type",
    type=click.Choice(["resources", "translations", "all"]),
    default="all",
)
def compile(path, res_type):
    """Compile resources and translations."""
    try:
        root = find_project_root(path)
        compile_qt_resources(root, res_type)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

@main.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
def clean(path):
    """Clean build artifacts."""
    try:
        root = find_project_root(path)
        clean_artifacts(root)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

if __name__ == "__main__":
    main()
