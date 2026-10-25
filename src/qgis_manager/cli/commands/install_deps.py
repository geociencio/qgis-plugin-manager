"""Install-deps command implementation."""

import argparse

import click

from ...dependencies import DependencyPolicy, install_external_libs
from ..base import BaseCommand


class InstallDepsCommand(BaseCommand):
    """Command to install plugin dependencies to a local folder."""

    examples = (
        "    # Install dependencies into the default 'libs' folder\n"
        "    qgis-manage install-deps\n\n"
        "    # Install into a custom target folder\n"
        "    qgis-manage install-deps --target vendor\n"
    )

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
        parser.add_argument(
            "--timeout",
            type=int,
            default=300,
            help="Maximum seconds for the dependency installer",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the installer command without running it",
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)
        policy = DependencyPolicy(timeout=args.timeout, dry_run=args.dry_run)
        if install_external_libs(root, args.target, policy=policy):
            click.echo("✨ Dependencies ready.")
            return 0
        else:
            return 1
