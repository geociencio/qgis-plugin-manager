"""Package command implementation."""

import argparse
from pathlib import Path

import click

from ...core import create_plugin_package
from ...dependencies import install_external_libs
from ...discovery import find_project_root
from ..base import BaseCommand


class PackageCommand(BaseCommand):
    """Command to create a distributable ZIP package."""

    @property
    def name(self) -> str:
        return "package"

    @property
    def help(self) -> str:
        return "Create distributable ZIP package"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser, include_profile=False)
        parser.add_argument("-o", "--output", help="Output directory for ZIP")
        parser.add_argument(
            "--dev", action="store_true", help="Include development files in package"
        )

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))

            # Auto-install deps if any are defined
            install_external_libs(root)

            with click.progressbar(
                length=100,
                label="📦 Packaging files",
                fill_char="#",
                empty_char="-",
                show_pos=True,
            ) as bar:

                def update_bar(n):
                    if bar.length == 100:
                        bar.length = n
                        bar.update(0)
                    else:
                        bar.update(n)

                zip_path = create_plugin_package(
                    root,
                    output_dir=Path(args.output) if args.output else None,
                    include_dev=args.dev,
                    callback=update_bar,
                )

            click.echo(click.style(f"✅ Package created: {zip_path}", fg="green"))
            return 0
        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
            return 1
