"""Validate command implementation."""

import argparse
import logging
from pathlib import Path

import click

from ...discovery import find_project_root, get_plugin_metadata
from ...validation import validate_metadata, validate_project_structure
from ..base import BaseCommand

logger = logging.getLogger(__name__)


class ValidateCommand(BaseCommand):
    """Command to validate metadata.txt compliance and project structure.

    Performs basic metadata checks and optionally checks for official
    QGIS repository compliance.
    """

    @property
    def name(self) -> str:
        """Command name as it appears in the CLI."""
        return "validate"

    @property
    def help(self) -> str:
        """Help text for the command."""
        return "Validate metadata.txt compliance and project structure"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-specific arguments.

        Args:
            parser: Argument parser to configure.
        """
        self.add_common_args(parser, include_profile=False)
        parser.add_argument("--strict", action="store_true", help="Fail on warnings")
        parser.add_argument(
            "--repo",
            action="store_true",
            help="Check compliance with official QGIS repository",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the validation command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success, 1 for failure).
        """
        try:
            root = find_project_root(Path(args.path))
            metadata = get_plugin_metadata(root)

            # 1. Metadata validation
            meta_result = validate_metadata(metadata)

            # 2. Structural validation
            struct_result = validate_project_structure(root, metadata)

            # 3. Official repo compliance (Optional)
            repo_errors: list[str] = []
            repo_warnings: list[str] = []
            if getattr(args, "repo", False):
                from ...validation import validate_official_compliance

                repo_res = validate_official_compliance(root)
                repo_errors = repo_res.errors
                repo_warnings = repo_res.warnings

            # Combine output
            errors = meta_result.errors + struct_result.errors + repo_errors
            warnings = meta_result.warnings + struct_result.warnings + repo_warnings
            is_valid = (
                meta_result.is_valid
                and struct_result.is_valid
                and (not getattr(args, "repo", False) or not repo_errors)
            )

            if errors:
                msg = click.style(
                    "❌ Validation failed with errors:", fg="red", bold=True
                )
                click.echo(msg, err=True)
                for error in errors:
                    logger.error(f"Validation Error: {error}")
                    click.echo(click.style(f"  • {error}", fg="red"), err=True)

            if warnings:
                click.echo(click.style("⚠️  Warnings:", fg="yellow", bold=True))
                for warning in warnings:
                    logger.warning(f"Validation Warning: {warning}")
                    click.echo(click.style(f"  • {warning}", fg="yellow"))

            if is_valid and not warnings:
                msg = click.style("✅ Plugin validation passed!", fg="green", bold=True)
                click.echo(msg)
            elif is_valid:
                msg = click.style(
                    "✅ Plugin validation passed (with warnings)", fg="green"
                )
                click.echo(msg)

            if args.strict and warnings:
                msg = "❌ Validation failed in strict mode due to warnings"
                logger.error(msg)
                click.echo(click.style(msg, fg="red"), err=True)
                return 1

            if not is_valid:
                logger.error("Validation failed.")
                click.echo(click.style("❌ Validation failed", fg="red"), err=True)
                return 1

            return 0

        except Exception as e:
            logger.error(f"Execution error in validate: {e}")
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
