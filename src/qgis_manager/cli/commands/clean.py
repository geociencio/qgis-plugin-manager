"""Clean command implementation."""

import argparse

from ...core import clean_artifacts
from .. import console
from ..base import BaseCommand


class CleanCommand(BaseCommand):
    """Command to clean build artifacts."""

    examples = "    # Clean Python cache and build artifacts\n    qgis-manage clean\n"

    @property
    def name(self) -> str:
        return "clean"

    @property
    def help(self) -> str:
        return "Remove Python cache files and build artifacts"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser, include_profile=False)
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be removed without deleting anything",
        )
        parser.add_argument(
            "--keep-generated",
            action="store_true",
            help="Preserve .py files generated from .ui/.qrc sources",
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)
        actions = clean_artifacts(
            root,
            dry_run=args.dry_run,
            keep_generated=args.keep_generated,
        )
        if args.dry_run:
            for action in actions:
                console.echo(action)
            console.echo("Dry run: no files were removed.")
        else:
            for action in actions:
                if action.startswith("warning:"):
                    console.echo(console.style(action, fg="yellow"), err=True)
        console.echo(console.style("✨ Cleanup complete!", fg="green", bold=True))
        return 0
