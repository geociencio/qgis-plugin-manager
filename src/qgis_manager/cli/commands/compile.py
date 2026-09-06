"""Compile command implementation."""

import argparse
from pathlib import Path

import click

from ...core import compile_qt_resources, count_compile_steps
from ...discovery import find_project_root
from ..base import BaseCommand
from ..progress import make_compile_callback


class CompileCommand(BaseCommand):
    """Command to compile Qt resources, translations, and documentation."""

    examples = (
        "    # Compile resources and translations\n"
        "    qgis-manage compile\n\n"
        "    # Compile only translations\n"
        "    qgis-manage compile --type translations\n"
    )

    @property
    def name(self) -> str:
        return "compile"

    @property
    def help(self) -> str:
        return "Compile resources and translations"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser, include_profile=False)
        parser.add_argument(
            "--type",
            dest="res_type",
            choices=["resources", "translations", "docs", "all"],
            default="all",
            help="Type of resources to compile (default: all)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))

            if args.res_type in ["docs", "all"]:
                total_steps = count_compile_steps(root, args.res_type)

                with click.progressbar(
                    length=total_steps, label="📚 Compilando", show_pos=True
                ) as bar:
                    compile_qt_resources(
                        root, args.res_type, callback=make_compile_callback(bar)
                    )
            else:
                compile_qt_resources(root, args.res_type)

            click.echo(click.style("✨ Compilation complete!", fg="green", bold=True))
            return 0
        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
