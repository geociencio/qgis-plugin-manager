"""Analyze command implementation."""

import argparse
import subprocess
from pathlib import Path

import click

from ...discovery import find_project_root
from ..base import BaseCommand


class AnalyzeCommand(BaseCommand):
    """Command to run QGIS Plugin Analyzer on the project."""

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

            # Check if qgis-analyzer is installed
            try:
                subprocess.run(
                    ["qgis-analyzer", "--version"], capture_output=True, check=True
                )
                cmd = ["qgis-analyzer", "analyze", str(root)]
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Try via uv run
                cmd = ["uv", "run", "qgis-analyzer", "analyze", str(root)]

            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                click.echo("❌ Analysis failed.")
                return result.returncode

            return 0

        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            return 1
