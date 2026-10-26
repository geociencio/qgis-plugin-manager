"""Security audit command implementation."""

import argparse
import json
from pathlib import Path

import click

from ..analyzer import run_qgis_analyzer, run_qgis_analyzer_output
from ..base import BaseCommand
from ..json_output import emit_json


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
        parser.add_argument(
            "--portal",
            action="store_true",
            help="Run Bandit/detect-secrets/Flake8 plus native rules",
        )
        parser.add_argument(
            "--exclude",
            action="append",
            default=[],
            help="Additional analyzer exclude pattern (repeatable)",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit a machine-readable security report",
        )
        parser.add_argument(
            "--fail-on",
            choices=["critical", "warning", "info", "none"],
            default="critical",
            help="Portal security failure threshold (default: critical)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)
        if not args.json:
            click.echo(f"🔒 Running security scan on {root}...")
        analyzer_args = self._analyzer_args(args)
        if args.json or args.portal:
            return self._run_machine(root, args, analyzer_args)
        code = run_qgis_analyzer(root, "security", *analyzer_args)
        if code != 0:
            click.echo("❌ Security scan found issues.")
            return code
        return 0

    def _analyzer_args(self, args: argparse.Namespace) -> list[str]:
        analyzer_args = ["--deep"]
        if args.strict:
            analyzer_args.append("--strict")
        if args.output:
            analyzer_args += ["-o", args.output]
        if args.portal:
            analyzer_args += [
                "--tools",
                "native,bandit,detect-secrets,flake8",
                "--fail-on",
                args.fail_on,
            ]
        for pattern in args.exclude:
            analyzer_args += ["--exclude", pattern]
        return analyzer_args

    def _run_machine(
        self,
        root: Path,
        args: argparse.Namespace,
        analyzer_args: list[str],
    ) -> int:
        code, output = run_qgis_analyzer_output(
            root, "security", *analyzer_args, "--json"
        )
        payload = None
        if output.strip():
            try:
                payload = json.loads(output)
            except json.JSONDecodeError:
                click.echo("❌ Analyzer returned invalid JSON.", err=True)
                return 2
        if args.json:
            emit_json(
                "security",
                code == 0 and payload is not None,
                errors=[] if code == 0 else [f"security exit code {code}"],
                data={"exit_code": code, "analyzer": payload},
            )
        elif payload is not None:
            click.echo(json.dumps(payload, indent=2))
        return code
