"""Package command implementation."""

import argparse
from pathlib import Path

import click

from ...core import create_plugin_package
from ...dependencies import install_external_libs
from ...discovery import find_project_root, sync_metadata_version
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

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))

            # 1. Version Sync (Optional)
            if getattr(args, "sync_version", False):
                py_version = get_project_version(root / "pyproject.toml")
                if py_version:
                    click.echo(f"🔄 Syncing version to {py_version}...")
                    sync_metadata_version(root)

            # 2. Compliance Check (Optional)
            if getattr(args, "repo_check", False):
                from ...discovery import get_plugin_metadata as fetch_metadata
                from ...validation import (
                    validate_metadata,
                    validate_official_compliance,
                    validate_project_structure,
                )

                click.echo("🔍 Running official repository compliance check...")
                metadata = fetch_metadata(root)
                meta_res = validate_metadata(metadata)
                repo_res = validate_official_compliance(root)
                struct_res = validate_project_structure(root, metadata)

                if not (
                    meta_res.is_valid and repo_res.is_valid and struct_res.is_valid
                ):
                    click.echo(
                        click.style(
                            "❌ Package compliance failed:", fg="red", bold=True
                        )
                    )
                    for err in meta_res.errors + repo_res.errors + struct_res.errors:
                        click.echo(f"  • {err}")
                    return 1
                click.echo(click.style("✅ Compliance check passed!", fg="green"))

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
                    stamp=getattr(args, "stamp", False),
                    release_version=getattr(args, "release_version", None),
                )

            click.echo(click.style(f"✅ Package created: {zip_path}", fg="green"))
            return 0
        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
            return 1
