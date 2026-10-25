"""Validate command implementation."""

import argparse
import logging

import click

from ...metadata import get_plugin_metadata
from ...validation import validate_metadata, validate_project_structure
from ..base import BaseCommand
from ..json_output import emit_json

logger = logging.getLogger(__name__)


class ValidateCommand(BaseCommand):
    """Command to validate metadata.txt compliance and project structure.

    Performs basic metadata checks and optionally checks for official
    QGIS repository compliance.
    """

    examples = (
        "    # Run deep structural validation\n"
        "    qgis-manage validate --strict --repo\n"
    )

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
            "--json",
            action="store_true",
            help="Emit machine-readable JSON on stdout",
        )
        parser.add_argument(
            "--repo",
            action="store_true",
            help="Check compliance with official QGIS repository",
        )

    def _emit_validation(
        self,
        args: argparse.Namespace,
        errors: list[str],
        warnings: list[str],
        is_valid: bool,
    ) -> int:
        """Render validation results and return the exit code."""
        if getattr(args, "json", False):
            success = is_valid and not (args.strict and warnings)
            emit_json(
                "validate",
                success,
                errors=errors,
                warnings=warnings,
                data={"valid": is_valid, "strict": args.strict},
            )
            return 0 if success else 1

        if errors:
            msg = click.style("❌ Validation failed with errors:", fg="red", bold=True)
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
            msg = click.style("✅ Plugin validation passed (with warnings)", fg="green")
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

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the validation command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success, 1 for failure).
        """
        root = self.project_root(args)
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

            repo_res = validate_official_compliance(root, metadata)
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

        return self._emit_validation(args, errors, warnings, is_valid)
