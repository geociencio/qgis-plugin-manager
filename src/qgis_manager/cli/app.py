"""CLI Application orchestrator."""

import argparse
import logging
import sys

from .base import BaseCommand

logger = logging.getLogger(__name__)


class CLIApp:
    """Main CLI application orchestrator.

    Manages command registration, argument parsing, and execution.
    """

    def __init__(self) -> None:
        """Initialize the CLI application with available commands."""
        self.commands: dict[str, BaseCommand] = self._discover_commands()

    def _discover_commands(self) -> dict[str, BaseCommand]:
        """Auto-discover and instantiate all command classes.

        Returns:
            Dictionary mapping command names to command instances.
        """
        from .commands.analyze import AnalyzeCommand
        from .commands.bump import BumpCommand
        from .commands.clean import CleanCommand
        from .commands.compile import CompileCommand
        from .commands.deploy import DeployCommand
        from .commands.hooks import HooksCommand
        from .commands.init import InitCommand
        from .commands.install_deps import InstallDepsCommand
        from .commands.package import PackageCommand
        from .commands.validate import ValidateCommand

        command_classes: list[type[BaseCommand]] = [
            DeployCommand,
            CompileCommand,
            PackageCommand,
            InitCommand,
            CleanCommand,
            AnalyzeCommand,
            ValidateCommand,
            InstallDepsCommand,
            HooksCommand,
            BumpCommand,
        ]
        return {cmd().name: cmd() for cmd in command_classes}

    def _build_parser(self) -> argparse.ArgumentParser:
        """Build the argument parser with all commands.

        Returns:
            Configured ArgumentParser instance.
        """
        from .. import __version__

        parser = argparse.ArgumentParser(
            description="QGIS Plugin Manager - Modern CLI for plugin development"
        )
        parser.add_argument(
            "-v", "--version", action="version", version=f"%(prog)s {__version__}"
        )
        parser.add_argument(
            "--verbose",
            "-V",
            action="count",
            default=0,
            help="Increase verbosity (can be used up to 3 times)",
        )
        parser.add_argument(
            "--log-file",
            help="Path to log file",
        )

        subparsers = parser.add_subparsers(dest="command", help="Command to execute")

        # Register all commands
        for cmd in self.commands.values():
            cmd_parser = subparsers.add_parser(cmd.name, help=cmd.help)
            cmd.configure_parser(cmd_parser)

        return parser

    def _setup_logging(self, args: argparse.Namespace) -> None:
        """Setup logging based on command arguments.

        Args:
            args: Parsed command-line arguments.
        """
        import logging

        level = logging.INFO
        if args.verbose == 1:
            level = logging.DEBUG
        elif args.verbose >= 2:
            level = logging.DEBUG

        log_format = "%(message)s"
        if args.verbose >= 1:
            log_format = "%(levelname)s: %(message)s"

        handlers: list[logging.Handler] = [logging.StreamHandler()]
        if args.log_file:
            handlers.append(logging.FileHandler(args.log_file))

        logging.basicConfig(level=level, format=log_format, handlers=handlers)

    def run(self, argv: list[str] | None = None) -> int:
        """Run the CLI application.

        Args:
            argv: Optional list of command-line arguments.

        Returns:
            Exit code (0 for success, 1 for failure).
        """
        parser = self._build_parser()

        if argv is None:
            argv = sys.argv[1:]

        try:
            args = parser.parse_args(argv)

            if not args.command:
                parser.print_help()
                return 0

            self._setup_logging(args)
            command = self.commands[args.command]
            return command.execute(args)

        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
            sys.stdout.write("\n⏹️ Interrupted.\n")
            return 1
        except Exception as e:
            logger.error(f"Top-level CLI error: {e}")
            import click

            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
