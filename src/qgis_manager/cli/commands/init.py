"""Init command implementation."""

import argparse
from pathlib import Path

import click

from ...core import init_plugin_project
from ..base import BaseCommand


class InitCommand(BaseCommand):
    """Command to initialize a new QGIS plugin project scaffolding."""

    @property
    def name(self) -> str:
        return "init"

    @property
    def help(self) -> str:
        return "Initialize a new QGIS plugin project scaffolding"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("name", help="Name of the plugin")
        parser.add_argument(
            "--path",
            default=".",
            help="Directory where the project folder will be created",
        )
        parser.add_argument("--author", help="Author of the plugin")
        parser.add_argument("--email", help="Author email")
        parser.add_argument(
            "--description", default="A QGIS plugin.", help="Plugin description"
        )
        parser.add_argument(
            "--template",
            default="default",
            help="Project template (default, processing, dockwidget)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        try:
            # Handle interactive prompts if information is missing
            author = args.author
            if not author:
                author = click.prompt("Author name")

            email = args.email
            if not email:
                email = click.prompt("Author email")

            init_plugin_project(
                Path(args.path),
                args.name,
                author,
                email,
                args.description,
                args.template,
            )
            msg = click.style(
                f"✅ Plugin '{args.name}' initialized successfully.",
                fg="green",
                bold=True,
            )
            click.echo(msg)
            return 0
        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
