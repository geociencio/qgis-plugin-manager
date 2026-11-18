"""QGIS profile discovery command."""

import argparse

from ...core import get_qgis_plugin_dir
from .. import console
from ..base import BaseCommand


class ProfilesCommand(BaseCommand):
    """List QGIS profiles and their installed plugin counts."""

    examples = "    # List profiles for QGIS 3\n    qgis-manage profiles list\n"

    @property
    def name(self) -> str:
        return "profiles"

    @property
    def help(self) -> str:
        return "List QGIS profiles and plugin counts"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--qgis-version",
            type=int,
            default=3,
            help="Major QGIS version (default: 3)",
        )
        subparsers = parser.add_subparsers(dest="action", metavar="ACTION")
        subparsers.add_parser("list", help="List profiles")

    def execute(self, args: argparse.Namespace) -> int:
        if args.action != "list":
            console.echo("❌ Use 'profiles list'.", err=True)
            return 1
        plugins_dir = get_qgis_plugin_dir("default", version=args.qgis_version)
        profiles_root = plugins_dir.parents[2]
        if not profiles_root.is_dir():
            console.echo("No QGIS profiles found.")
            return 0
        profiles = sorted(path for path in profiles_root.iterdir() if path.is_dir())
        if not profiles:
            console.echo("No QGIS profiles found.")
            return 0
        console.echo(f"Profiles for QGIS {args.qgis_version}:")
        for profile in profiles:
            plugins = profile / "python" / "plugins"
            count = (
                sum(1 for item in plugins.iterdir() if item.is_dir())
                if plugins.is_dir()
                else 0
            )
            console.echo(f"  {profile.name}\t{profile}\t{count} plugins")
        return 0
