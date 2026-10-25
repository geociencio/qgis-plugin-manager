"""Clean command implementation."""

import argparse

import click

from ...core import clean_artifacts
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

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)
        clean_artifacts(root)
        click.echo(click.style("✨ Cleanup complete!", fg="green", bold=True))
        return 0
