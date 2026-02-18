"""Clean command implementation."""

import argparse
from pathlib import Path

import click

from ...core import clean_artifacts
from ...discovery import find_project_root
from ..base import BaseCommand


class CleanCommand(BaseCommand):
    """Command to clean build artifacts."""

    @property
    def name(self) -> str:
        return "clean"

    @property
    def help(self) -> str:
        return "Remove Python cache files and build artifacts"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser, include_profile=False)

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))
            clean_artifacts(root)
            click.echo(click.style("✨ Cleanup complete!", fg="green", bold=True))
            return 0
        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
