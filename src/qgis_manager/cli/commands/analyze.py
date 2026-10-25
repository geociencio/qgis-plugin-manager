"""Analyze command implementation."""

import argparse

import click

from ..analyzer import run_qgis_analyzer
from ..base import BaseCommand
from ..json_output import emit_json


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
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit machine-readable JSON on stdout",
        )
        parser.add_argument(
            "--max-cc",
            type=int,
            default=None,
            help="Maximum cyclomatic complexity passed to qgis-analyzer",
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)
        if not args.json:
            click.echo(f"🔍 Analyzing project at {root}...")

        analyzer_args: list[str] = []
        if args.max_cc is not None:
            analyzer_args += ["--max-cc", str(args.max_cc)]
        code = run_qgis_analyzer(root, "analyze", *analyzer_args, capture=args.json)
        if args.json:
            emit_json(
                "analyze",
                code == 0,
                errors=[] if code == 0 else [f"qgis-analyzer exited {code}"],
                data={"exit_code": code},
            )
            return code
        if code != 0:
            click.echo("❌ Analysis failed.")
            return code

        return 0
