"""Compile command implementation."""

import argparse

import click

from ...core import compile_qt_resources, count_compile_steps
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
        return "Compile resources, UI files and translations"

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
        root = self.project_root(args)

        if args.res_type in ["docs", "all"]:
            total_steps = count_compile_steps(root, args.res_type)

            with click.progressbar(
                length=total_steps, label="📚 Compilando", show_pos=True
            ) as bar:
                compiled = compile_qt_resources(
                    root, args.res_type, callback=make_compile_callback(bar)
                )
        else:
            compiled = compile_qt_resources(root, args.res_type)

        if not compiled:
            click.echo(
                click.style(
                    "❌ Compilation failed. Check the errors above.",
                    fg="red",
                    bold=True,
                ),
                err=True,
            )
            return 1

        click.echo(click.style("✨ Compilation complete!", fg="green", bold=True))
        return 0
