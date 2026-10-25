"""Analyze command implementation."""

import argparse

import click

from ..analyzer import run_qgis_analyzer
from ..base import BaseCommand


class AnalyzeCommand(BaseCommand):
    """Command to run QGIS Plugin Analyzer on the project."""

    examples = "    # Run the QGIS plugin analyzer\n    qgis-manage analyze\n"

    @property
    def name(self) -> str:
        return "analyze"

    @property
    def help(self) -> str:
        return "Run QGIS Plugin Analyzer on the project"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser, include_profile=False)

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)
        click.echo(f"🔍 Analyzing project at {root}...")

        code = run_qgis_analyzer(root, "analyze")
        if code != 0:
            click.echo("❌ Analysis failed.")
            return code

        return 0
