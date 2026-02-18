"""Compile command implementation."""

import argparse
from pathlib import Path

import click

from ...core import compile_qt_resources
from ...discovery import find_project_root
from ..base import BaseCommand


class CompileCommand(BaseCommand):
    """Command to compile Qt resources, translations, and documentation."""

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
                qrc_count = (
                    len(list(root.rglob("*.qrc"))) if args.res_type == "all" else 0
                )
                ts_count = (
                    len(list(root.rglob("*.ts"))) if args.res_type == "all" else 0
                )
                has_docs = (root / "docs" / "source" / "conf.py").exists()
                total_steps = qrc_count + ts_count + (1 if has_docs else 0)

                with click.progressbar(
                    length=total_steps, label="📚 Compilando", show_pos=True
                ) as bar:

                    def comp_callback(line):
                        import time

                        icons = {"Recurso": "🔨", "Trad": "🌍", "Documentación": "📚"}
                        msg = line.split(":", 1)[1] if ":" in line else line
                        short_msg = msg[:40] + "..." if len(msg) > 40 else msg

                        if line.startswith("START:"):
                            icon = "🛠️"
                            for k, v in icons.items():
                                if k in msg:
                                    icon = v
                                    break
                            bar.label = f"{icon} {short_msg}"
                            bar.update(0)
                        elif line.startswith("PROGRESS:"):
                            spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
                            s = spinner[int(time.time() * 5) % len(spinner)]
                            bar.label = f"📚 {s} {short_msg}"
                            bar.update(0)
                        elif line.startswith("DONE:"):
                            bar.update(1)

                    compile_qt_resources(root, args.res_type, callback=comp_callback)
            else:
                compile_qt_resources(root, args.res_type)

            click.echo(click.style("✨ Compilation complete!", fg="green", bold=True))
            return 0
        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
