"""Bump command implementation."""

import argparse
import logging
import re
from pathlib import Path

import click

from ...discovery import find_project_root, get_plugin_metadata, save_plugin_metadata
from ..base import BaseCommand

logger = logging.getLogger(__name__)


class BumpCommand(BaseCommand):
    """Command to automate project versioning.

    Handles major, minor, and patch bumps, as well as syncing version
    from pyproject.toml to metadata.txt.
    """

    @property
    def name(self) -> str:
        """Command name as it appears in the CLI."""
        return "bump"

    @property
    def help(self) -> str:
        """Help text for the command."""
        return "Automate project versioning"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure subcommand and arguments.

        Args:
            parser: Argument parser to configure.
        """
        self.add_common_args(parser, include_profile=False)
        subparsers = parser.add_subparsers(dest="subcommand", help="Bump subcommand")

        subparsers.add_parser("major", help="Bump major version (X.y.z -> X+1.0.0)")
        subparsers.add_parser("minor", help="Bump minor version (x.Y.z -> x.Y+1.0)")
        subparsers.add_parser("patch", help="Bump patch version (x.y.Z -> x.y.Z+1)")
        subparsers.add_parser(
            "sync", help="Sync metadata.txt with pyproject.toml version"
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the bump command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success, 1 for failure).
        """
        try:
            root = find_project_root(Path(args.path))

            if args.subcommand in ["major", "minor", "patch"]:
                return self._bump_version(root, args.subcommand)
            elif args.subcommand == "sync":
                return self._sync_versions(root)
            else:
                click.echo(
                    click.style(
                        "❌ No subcommand specified. Use --help for usage.", fg="red"
                    )
                )
                return 1
        except Exception as e:
            logger.error(f"Execution error in bump: {e}")
            click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
            return 1

    def _bump_version(self, root: Path, part: str) -> int:
        """Bump a part of the semantic version.

        Args:
            root: Project root directory.
            part: Part of the version to bump (major, minor, or patch).

        Returns:
            Exit code.
        """
        current = self._get_version(root)
        if not current:
            logger.error(f"Could not determine current version in {root}")
            click.echo(click.style("❌ Could not determine current version.", fg="red"))
            return 1

        parts = current.split(".")
        if len(parts) < 3:
            # Pad with zeros if needed
            parts = (parts + ["0", "0", "0"])[:3]

        try:
            major, minor, patch = map(int, parts)
        except ValueError as e:
            logger.error(f"Invalid version format '{current}': {e}")
            click.echo(click.style(f"❌ Invalid version format: {current}", fg="red"))
            return 1

        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        elif part == "patch":
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        click.echo(f"⬆️ Bumping {part}: {current} -> {new_version}")

        # Update all files
        updated = self._update_version_in_files(root, new_version)
        if updated:
            click.echo(click.style(f"✅ Version bumped to {new_version}", fg="green"))
            return 0
        else:
            logger.error(f"Failed to update version entries to {new_version}")
            click.echo(click.style("❌ Failed to update version in files.", fg="red"))
            return 1

    def _sync_versions(self, root: Path) -> int:
        """Sync version from pyproject.toml to metadata.txt.

        Args:
            root: Project root directory.

        Returns:
            Exit code.
        """
        version = self._get_pyproject_version(root)
        if not version:
            click.echo(click.style("❌ No version found in pyproject.toml", fg="red"))
            return 1

        click.echo(f"🔄 Syncing version {version} to metadata.txt...")
        metadata = get_plugin_metadata(root)
        if metadata.get("version") != version:
            metadata["version"] = version
            save_plugin_metadata(root, metadata)
            click.echo(click.style("✅ metadata.txt updated.", fg="green"))
        else:
            click.echo("✅ Already in sync.")

        return 0

    def _get_version(self, root: Path) -> str | None:
        """Get version from pyproject.toml or metadata.txt.

        Args:
            root: Project root directory.

        Returns:
            Version string or None if not found.
        """
        v = self._get_pyproject_version(root)
        if v:
            return v
        metadata = get_plugin_metadata(root)
        return metadata.get("version")

    def _get_pyproject_version(self, root: Path) -> str | None:
        """Read version from pyproject.toml.

        Args:
            root: Project root directory.

        Returns:
            Version string or None.
        """
        pyproj = root / "pyproject.toml"
        if not pyproj.exists():
            return None
        import tomllib

        try:
            with open(pyproj, "rb") as f:
                data = tomllib.load(f)
                version = data.get("project", {}).get("version")
                return str(version) if version else None
        except Exception as e:
            logger.debug(f"Failed to read pyproject.toml version: {e}")
            return None

    def _update_version_in_files(self, root: Path, version: str) -> bool:
        """Update version in all tracked files.

        Args:
            root: Project root directory.
            version: New version string to set.

        Returns:
            True if all updates succeeded.
        """
        success = True

        # 1. Update pyproject.toml
        pyproj = root / "pyproject.toml"
        if pyproj.exists():
            content = pyproj.read_text(encoding="utf-8")
            # Try to find version in [project] section safely
            match = re.search(
                r"(\[project\].*?version\s*=\s*\")[^\"]+(\")", content, re.DOTALL
            )
            if match:
                new_content = (
                    content[: match.start(0)]
                    + match.group(1)
                    + version
                    + match.group(2)
                    + content[match.end(0) :]
                )
                pyproj.write_text(new_content, encoding="utf-8")
                click.echo("  📝 Updated pyproject.toml")
            else:
                # Fallback to simple replacement
                new_content = re.sub(
                    r"(version\s*=\s*\")[^\"]+(\")", rf"\1{version}\2", content, count=1
                )
                if new_content != content:
                    pyproj.write_text(new_content, encoding="utf-8")
                    click.echo("  📝 Updated pyproject.toml (simple match)")
                else:
                    logger.warning("Could not find version entry in pyproject.toml")
                    success = False

        # 2. Update metadata.txt
        try:
            metadata = get_plugin_metadata(root)
            metadata["version"] = version
            save_plugin_metadata(root, metadata)
            click.echo("  📝 Updated metadata.txt")
        except Exception as e:
            logger.error(f"Error updating metadata.txt: {e}")
            click.echo(click.style(f"  ❌ Error updating metadata.txt: {e}", fg="red"))
            success = False

        return success
