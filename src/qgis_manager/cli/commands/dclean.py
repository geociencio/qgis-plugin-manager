"""Remove deployed plugin command implementation."""

import argparse
from pathlib import Path

import click

from ...config import load_config, load_project_config
from ...core import uninstall_plugin
from ...discovery import find_project_root
from ..base import BaseCommand


class DCleanCommand(BaseCommand):
    """Command to remove the deployed plugin from a QGIS profile."""

    examples = (
        "    # Remove the plugin from the default QGIS profile\n"
        "    qgis-manage dclean\n\n"
        "    # Remove from a QGIS 4 profile without confirmation\n"
        "    qgis-manage dclean --qgis-version 4 --yes\n"
    )

    @property
    def name(self) -> str:
        return "dclean"

    @property
    def help(self) -> str:
        return "Remove the deployed plugin from the QGIS profile"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser)
        parser.add_argument(
            "--qgis-version",
            type=int,
            help="Major QGIS version (3 or 4)",
        )
        parser.add_argument(
            "--yes",
            "-y",
            action="store_true",
            help="Remove without asking for confirmation",
        )

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))

            settings = load_config()
            settings = load_project_config(root, settings)

            target_profile = args.profile or settings.profile
            qgis_version = args.qgis_version or settings.qgis_version

            if not args.yes and not click.confirm(
                f"🗑️  Remove the deployed plugin from profile "
                f"'{target_profile}' (QGIS {qgis_version})?"
            ):
                click.echo("Aborted.")
                return 0

            removed = uninstall_plugin(
                root, profile=target_profile, qgis_version=qgis_version
            )

            if removed:
                click.echo(click.style(f"🗑️  Removed {removed}", fg="green"))
            else:
                click.echo("Plugin not deployed. Nothing to remove.")
            return 0
        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
