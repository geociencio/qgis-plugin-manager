"""Ignore rule inspection command."""

import argparse
from pathlib import Path

import click

from ...ignore import IgnoreMatcher
from ..base import BaseCommand


class IgnoreCommand(BaseCommand):
    """Check whether a path is excluded and explain the winning rule."""

    examples = (
        "    # Check a path against project ignore rules\n"
        "    qgis-manage ignore check tests/tmp.txt\n\n"
        "    # Show the rule that wins\n"
        "    qgis-manage ignore check tests/tmp.txt --explain\n"
    )

    @property
    def name(self) -> str:
        return "ignore"

    @property
    def help(self) -> str:
        return "Check ignore rules for a path"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--project",
            dest="path",
            default=".",
            help="Project root (default: current directory)",
        )
        subparsers = parser.add_subparsers(dest="action", metavar="ACTION")
        check = subparsers.add_parser("check", help="Check one path")
        check.add_argument("target", help="Path relative to the project root")
        check.add_argument(
            "--explain",
            action="store_true",
            help="Print the winning ignore rule",
        )

    def execute(self, args: argparse.Namespace) -> int:
        if args.action != "check":
            click.echo("❌ Use 'ignore check <path>'.", err=True)
            return 1
        root = self.project_root(args)
        target = Path(args.target)
        if not target.is_absolute():
            target = root / target
        excluded, rule = IgnoreMatcher(root).explain(target)
        decision = "excluded" if excluded else "included"
        if args.explain:
            click.echo(f"{decision}: {target}")
            click.echo(f"rule: {rule or 'no matching rule'}")
        else:
            click.echo(decision)
        return 0 if excluded else 1
