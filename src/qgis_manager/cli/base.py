"""Base command class for CLI commands."""

import argparse
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Abstract base class for CLI commands.

    Each command encapsulates its own argument configuration and execution logic.
    """

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
                help="QGIS profile name (default: default)",
                default="default",
            )
