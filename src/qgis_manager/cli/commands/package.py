"""Package command implementation."""

import argparse
from pathlib import Path

import click

from ...core import create_plugin_package
from ...dependencies import get_dependencies, install_external_libs
from ...metadata import get_plugin_metadata, sync_metadata_version
from ...toml_utils import get_project_version
from ..base import BaseCommand


class PackageCommand(BaseCommand):
    """Command to create a distributable ZIP package."""

    examples = (
        "    # Create a ZIP package\n"
        "    qgis-manage package\n\n"
        "    # Package with strict compliance check and version sync\n"
        "    qgis-manage package --repo-check --sync-version\n\n"
        "    # Stamp git build info into the packaged metadata.txt\n"
        "    qgis-manage package --stamp\n"
    )

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
        parser.add_argument(
            "--repo-check",
            action="store_true",
            help="Strictly validate official repository compliance before packaging",
        )
        parser.add_argument(
            "--sync-version",
            action="store_true",
            help="Sync metadata.txt version from pyproject.toml",
        )
        parser.add_argument(
            "--stamp",
            action="store_true",
            help="Inject build metadata (git SHA, datetime, experimental) "
            "into the packaged metadata.txt",
        )
        parser.add_argument(
            "--release-version",
            help="Override the version used for the ZIP name and stamping",
        )
        parser.add_argument(
            "--trust",
            action="store_true",
            help="Allow dependency installation from this project (trusted only)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)
        self._sync_version(root, args)
        if not self._validate_release_version(root, args):
            return 1
        if not self._install_dependencies(root, args):
            return 1
        if not self._check_compliance(root, args):
            return 1
        zip_path = self._build_package(root, args)
        click.echo(click.style(f"✅ Package created: {zip_path}", fg="green"))
        return 0

    def _sync_version(self, root: Path, args: argparse.Namespace) -> None:
        if not args.sync_version:
            return
        py_version = get_project_version(root / "pyproject.toml")
        if py_version:
            click.echo(f"🔄 Syncing version to {py_version}...")
            sync_metadata_version(root)

    def _validate_release_version(self, root: Path, args: argparse.Namespace) -> bool:
        if not args.release_version:
            return True
        current = get_plugin_metadata(root).get("version")
        if args.stamp or current == args.release_version:
            return True
        click.echo(
            click.style(
                f"❌ --release-version {args.release_version} does not match "
                f"metadata.txt ({current or 'missing'}); use --stamp or "
                "--sync-version.",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        return False

    def _install_dependencies(self, root: Path, args: argparse.Namespace) -> bool:
        dependencies = get_dependencies(root)
        if dependencies and not args.trust:
            click.echo(
                click.style(
                    "❌ Project declares dependencies; re-run with --trust "
                    "to allow installation.",
                    fg="red",
                    bold=True,
                ),
                err=True,
            )
            return False
        if not install_external_libs(root):
            click.echo(
                click.style(
                    "❌ Dependency installation failed; aborting package.",
                    fg="red",
                    bold=True,
                ),
                err=True,
            )
            return False
        return True

    def _check_compliance(self, root: Path, args: argparse.Namespace) -> bool:
        if not args.repo_check:
            return True
        from ...metadata import get_plugin_metadata as fetch_metadata
        from ...validation import (
            validate_metadata,
            validate_official_compliance,
            validate_project_structure,
        )

        click.echo("🔍 Running official repository compliance check...")
        metadata = fetch_metadata(root)
        meta_res = validate_metadata(metadata)
        repo_res = validate_official_compliance(root, metadata)
        struct_res = validate_project_structure(root, metadata)
        if meta_res.is_valid and repo_res.is_valid and struct_res.is_valid:
            click.echo(click.style("✅ Compliance check passed!", fg="green"))
            return True
        click.echo(click.style("❌ Package compliance failed:", fg="red", bold=True))
        for err in meta_res.errors + repo_res.errors + struct_res.errors:
            click.echo(f"  • {err}")
        return False

    def _build_package(self, root: Path, args: argparse.Namespace) -> Path:
        with click.progressbar(
            length=100,
            label="📦 Packaging files",
            fill_char="#",
            empty_char="-",
            show_pos=True,
        ) as bar:

            def update_bar(n: int) -> None:
                if bar.length == 100:
                    bar.length = n
                    bar.update(0)
                else:
                    bar.update(n)

            return create_plugin_package(
                root,
                output_dir=Path(args.output) if args.output else None,
                include_dev=args.dev,
                callback=update_bar,
                stamp=args.stamp,
                release_version=args.release_version,
            )
