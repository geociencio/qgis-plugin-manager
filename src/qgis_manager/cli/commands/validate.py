"""Validate command implementation."""

import argparse
from pathlib import Path

import click

from ...discovery import find_project_root, get_plugin_metadata
from ...validation import validate_metadata, validate_project_structure
from ..base import BaseCommand


class ValidateCommand(BaseCommand):
    """Command to validate metadata.txt compliance and project structure."""

    @property
    def name(self) -> str:
        return "validate"

    @property
    def help(self) -> str:
        return "Validate metadata.txt compliance and project structure"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser, include_profile=False)
        parser.add_argument("--strict", action="store_true", help="Fail on warnings")

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))
            metadata = get_plugin_metadata(root)

            # 1. Metadata validation
            meta_result = validate_metadata(metadata)

            # 2. Structural validation
            struct_result = validate_project_structure(root, metadata)

            # Combine output
            errors = meta_result.errors + struct_result.errors
            warnings = meta_result.warnings + struct_result.warnings
            is_valid = meta_result.is_valid and struct_result.is_valid

            if errors:
                msg = click.style(
                    "❌ Validation failed with errors:", fg="red", bold=True
                )
                click.echo(msg, err=True)
                for error in errors:
                    click.echo(click.style(f"  • {error}", fg="red"), err=True)

            if warnings:
                click.echo(click.style("⚠️  Warnings:", fg="yellow", bold=True))
                for warning in warnings:
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
                click.echo(
                    click.style(
                        "❌ Validation failed in strict mode due to warnings", fg="red"
                    ),
                    err=True,
                )
                return 1

            if not is_valid:
                click.echo(click.style("❌ Validation failed", fg="red"), err=True)
                return 1

            return 0

        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
