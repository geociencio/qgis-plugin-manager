"""Analyze command implementation."""

import argparse
from pathlib import Path

import click

from ...discovery import find_project_root
from ..analyzer import run_qgis_analyzer
from ..base import BaseCommand


class AnalyzeCommand(BaseCommand):
    """Command to run QGIS Plugin Analyzer on the project."""

    examples = (
        "    # Run the QGIS plugin analyzer\n"
        "    qgis-manage analyze\n"
    )

    @property
    def name(self) -> str:
        return "analyze"

    @property
    def help(self) -> str:
        return "Run QGIS Plugin Analyzer on the project"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser, include_profile=False)

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))
            click.echo(f"🔍 Analyzing project at {root}...")

            code = run_qgis_analyzer(root, "analyze")
            if code != 0:
                click.echo("❌ Analysis failed.")
                return code

            return 0

        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            return 1
