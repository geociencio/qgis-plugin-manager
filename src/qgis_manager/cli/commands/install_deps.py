"""Install-deps command implementation."""

import argparse
from pathlib import Path

import click

from ...dependencies import install_external_libs
from ...discovery import find_project_root
from ..base import BaseCommand


class InstallDepsCommand(BaseCommand):
    """Command to install plugin dependencies to a local folder."""

    @property
    def name(self) -> str:
        return "install-deps"

    @property
    def help(self) -> str:
        return "Install plugin dependencies to a local folder"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--path", default=".", help="Project root directory")
        parser.add_argument(
            "--target", default="libs", help="Target directory for libraries"
        )

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))
            if install_external_libs(root, args.target):
                click.echo("✨ Dependencies ready.")
                return 0
            else:
                return 1
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            return 1
