"""Security audit command implementation."""

import argparse
from pathlib import Path

import click

from ...discovery import find_project_root
from ..analyzer import run_qgis_analyzer
from ..base import BaseCommand


class SecurityCommand(BaseCommand):
    """Command to run a focused security audit on the project."""

    examples = (
        "    # Scan for secrets and PyQGIS security issues\n"
        "    qgis-manage security\n\n"
        "    # Scan with strict gold-standard rules\n"
        "    qgis-manage security --strict\n"
    )

    @property
    def name(self) -> str:
        return "security"

    @property
    def help(self) -> str:
        return "Run a security audit (secrets and PyQGIS rules)"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser, include_profile=False)
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict gold-standard rules",
        )
        parser.add_argument(
            "-o",
            "--output",
            help="Output directory for reports",
        )

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))
            click.echo(f"🔒 Running security scan on {root}...")

            analyzer_args = ["--deep"]
            if args.strict:
                analyzer_args.append("--strict")
            if args.output:
                analyzer_args += ["-o", args.output]

            code = run_qgis_analyzer(root, "security", *analyzer_args)
            if code != 0:
                click.echo("❌ Security scan found issues.")
                return code

            return 0

        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            return 1
