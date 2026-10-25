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
            "--jobs",
            type=int,
            default=1,
            help="Number of files to compile concurrently (default: 1)",
        )
        parser.add_argument(
            "--type",
            dest="res_type",
            action="append",
            choices=["resources", "translations", "docs", "all"],
            help="Type of resources to compile; may be repeated (default: all)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)
        requested = args.res_type or ["all"]
        selected = ["all"] if "all" in requested else list(dict.fromkeys(requested))
        compile_arg = selected[0] if len(selected) == 1 else selected

        if any(item in ("docs", "all") for item in selected):
            total_steps = count_compile_steps(root, selected)

            with click.progressbar(
                length=total_steps, label="📚 Compilando", show_pos=True
            ) as bar:
                compiled = compile_qt_resources(
                    root,
                    compile_arg,
                    callback=make_compile_callback(bar),
                    jobs=args.jobs,
                )
        else:
            compiled = compile_qt_resources(root, compile_arg, jobs=args.jobs)

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
