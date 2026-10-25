"""Base command class for CLI commands."""

import argparse
from abc import ABC, abstractmethod
from pathlib import Path

import click

from ..discovery import find_project_root


class BaseCommand(ABC):
    """Abstract base class for CLI commands.

    Each command encapsulates its own argument configuration and execution logic.
    """

    #: Usage examples rendered at the bottom of the command's ``--help`` output.
    examples: str = ""

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name as it appears in the CLI."""

    @property
    @abstractmethod
    def help(self) -> str:
        """Help text for the command."""

    @abstractmethod
    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-specific arguments."""

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """Execute the command."""

    def project_root(self, args: argparse.Namespace) -> Path:
        """Resolve the project root from the common ``path`` argument."""
        return find_project_root(Path(args.path))

    def run(self, args: argparse.Namespace) -> int:
        """Run the command, mapping unexpected errors to a CLI exit code."""
        try:
            return self.execute(args)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            click.echo(click.style(f"❌ Error: {exc}", fg="red", bold=True), err=True)
            return 1

    def add_common_args(
        self,
        parser: argparse.ArgumentParser,
        include_path: bool = True,
        include_profile: bool = True,
    ) -> None:
        """Add common arguments shared across multiple commands."""
        if include_path:
            parser.add_argument(
                "path",
                nargs="?",
                default=".",
                help="Project directory path (default: current directory)",
            )
        if include_profile:
            parser.add_argument(
                "-p",
                "--profile",
                help=(
                    "QGIS profile name or absolute plugins directory "
                    "(default: configured profile, else 'default')"
                ),
                default=None,
            )
