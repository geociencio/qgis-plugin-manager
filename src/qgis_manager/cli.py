# /***************************************************************************
#  QGIS Plugin Manager
#                                  A CLI Tool
#  Modern command-line interface for QGIS plugin development and deployment.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
Command-line interface for QGIS plugin management.

This module provides Click-based CLI commands for deploying plugins to QGIS,
compiling Qt resources and translations, and cleaning build artifacts.

Commands:
    deploy: Deploy plugin to local QGIS profile with automatic backup
    compile: Compile Qt resources (.qrc) and translations (.ts)
    clean: Remove Python cache files and build artifacts
    package: Create distributable ZIP package
    validate: Validate metadata.txt compliance
    init: Initialize a new QGIS plugin project scaffolding
"""

import logging
from pathlib import Path

import click

from .config import load_config, load_project_config
from .core import (
    clean_artifacts,
    compile_qt_resources,
    create_plugin_package,
    deploy_plugin,
    get_qgis_plugin_dir,
    init_plugin_project,
)
from .discovery import find_project_root, get_plugin_metadata
from .hooks import run_hook
from .validation import validate_metadata


@click.group()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (can be used up to 3 times)",
)
@click.option("--log-file", type=click.Path(path_type=Path), help="Path to log file")
def main(verbose, log_file):
    """Modern CLI for QGIS plugin development."""
    level = logging.INFO
    if verbose == 1:
        level = logging.DEBUG
    elif verbose >= 2:
        level = logging.DEBUG  # Can add CUSTOM levels if needed for -vvv

    log_format = "%(message)s"
    if verbose >= 1:
        log_format = "%(levelname)s: %(message)s"

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(level=level, format=log_format, handlers=handlers)


@main.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option("--no-backup", is_flag=True, help="Skip backup of existing installation.")
@click.option("-p", "--profile", help="QGIS profile to deploy to (overrides config)")
@click.option(
    "-i", "--interactive", is_flag=True, help="Ask for confirmation before each step"
)
@click.option("--no-compile", is_flag=True, help="Saltar compilación automática.")
def deploy(path, no_backup, profile, interactive, no_compile):
    """Deploy the plugin to the local QGIS profile."""
    try:
        root = find_project_root(path)

        # Load config
        settings = load_config()
        settings = load_project_config(root, settings)

        # Defaults
        target_profile = profile or settings.profile
        use_backup = not no_backup if no_backup else settings.backup

        # Pre-deploy hook
        pre_hook = settings.hooks.get("pre-deploy")
        if pre_hook:
            if interactive:
                if not click.confirm(f"🪝  Execute pre-deploy hook: {pre_hook}?"):
                    click.echo("⏭️  Skipping hook.")
                    pre_hook = None

            if pre_hook:
                if not run_hook("pre-deploy", pre_hook, root):
                    raise click.Abort()

        if interactive:
            if not click.confirm(f"🚀 Deploy to profile '{target_profile}'?"):
                click.echo("Aborted by user.")
                raise click.Abort()

        if not no_compile and settings.auto_compile:
            with click.progressbar(
                length=0, label="📚 Compilando recursos y docus", show_percent=False
            ) as bar:

                def doc_callback(line):
                    # Truncar línea para el label si es muy larga
                    msg = line[:40] + "..." if len(line) > 40 else line
                    bar.label = f"📚 {msg}"
                    bar.update(0)

                compile_qt_resources(root, "all", callback=doc_callback)

        # Pre-info
        metadata = get_plugin_metadata(root)
        slug = metadata["slug"]
        target_path = (
            Path(profile)
            if profile and Path(profile).is_absolute()
            else get_qgis_plugin_dir(target_profile) / slug
        )
        click.echo(f"🚀 Deploying '{metadata['name']}' ({slug}) to {target_path}")

        # Logic with progress bar
        with click.progressbar(
            length=100,
            label="📦 Copying files",
            fill_char="#",
            empty_char="-",
            show_pos=True,
        ) as bar:

            def update_bar(n):
                if bar.length == 100:  # Initial dummy length
                    bar.length = n
                    bar.update(0)  # Initial refresh
                else:
                    bar.update(n)

            deploy_plugin(
                root,
                no_backup=not use_backup,
                profile=target_profile,
                callback=update_bar,
            )

        # Post-deploy hook
        post_hook = settings.hooks.get("post-deploy")
        if post_hook:
            if interactive:
                if not click.confirm(f"🪝  Execute post-deploy hook: {post_hook}?"):
                    click.echo("⏭️  Skipping hook.")
                    post_hook = None

            if post_hook:
                run_hook("post-deploy", post_hook, root)

        click.echo(click.style("✨ Deployment complete!", fg="green", bold=True))

    except Exception as e:
        if not isinstance(e, click.Abort):
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            if "metadata.txt" in str(e):
                click.echo(
                    click.style(
                        "💡 Hint: Ensure you are in the plugin root directory.",
                        fg="cyan",
                    )
                )
        raise click.Abort() from e


@main.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--type",
    "res_type",
    type=click.Choice(["resources", "translations", "docs", "all"]),
    default="all",
)
def compile(path, res_type):
    """Compile resources and translations."""
    try:
        root = find_project_root(path)
        if res_type in ["docs", "all"]:
            with click.progressbar(
                length=0, label="📚 Compilando documentación", show_percent=False
            ) as bar:

                def doc_callback(line):
                    msg = line[:40] + "..." if len(line) > 40 else line
                    bar.label = f"📚 {msg}"
                    bar.update(0)

                compile_qt_resources(root, res_type, callback=doc_callback)
        else:
            compile_qt_resources(root, res_type)

        click.echo(click.style("✨ Compilation complete!", fg="green", bold=True))
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
        raise click.Abort() from e


@main.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
def clean(path):
    """Clean build artifacts."""
    try:
        root = find_project_root(path)
        clean_artifacts(root)
        click.echo(click.style("✨ Cleanup complete!", fg="green", bold=True))
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
        raise click.Abort() from e


@main.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output directory for ZIP"
)
@click.option("--dev", is_flag=True, help="Include development files in package")
def package(path, output, dev):
    """Create distributable ZIP package."""
    try:
        root = find_project_root(path)

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
                root, output_dir=output, include_dev=dev, callback=update_bar
            )

        click.echo(click.style(f"✅ Package created: {zip_path}", fg="green"))
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        raise click.Abort() from e


@main.command()
@click.argument(
    "path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option("--strict", is_flag=True, help="Fail on warnings")
def validate(path, strict):
    """Validate metadata.txt compliance."""
    try:
        root = find_project_root(path)
        metadata = get_plugin_metadata(root)
        result = validate_metadata(metadata)

        if result.errors:
            msg = click.style("❌ Validation failed with errors:", fg="red", bold=True)
            click.echo(msg, err=True)
            for error in result.errors:
                click.echo(click.style(f"  • {error}", fg="red"), err=True)

        if result.warnings:
            click.echo(click.style("⚠️  Warnings:", fg="yellow", bold=True))
            for warning in result.warnings:
                click.echo(click.style(f"  • {warning}", fg="yellow"))

        if result.is_valid and not result.warnings:
            msg = click.style("✅ Metadata validation passed!", fg="green", bold=True)
            click.echo(msg)
        elif result.is_valid:
            msg = click.style(
                "✅ Metadata validation passed (with warnings)", fg="green"
            )
            click.echo(msg)

        if strict and result.warnings:
            raise click.ClickException(
                "Validation failed in strict mode due to warnings"
            )

        if not result.is_valid:
            raise click.ClickException("Validation failed")

    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
        raise click.Abort() from e


@main.command()
@click.argument("name")
@click.option(
    "--path",
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory where the project folder will be created",
)
@click.option("--author", required=True, help="Author of the plugin")
@click.option("--email", required=True, help="Author email")
@click.option("--description", default="A QGIS plugin.", help="Plug-in description")
def init(name, path, author, email, description):
    """Initialize a new QGIS plugin project scaffolding."""
    try:
        init_plugin_project(path, name, author, email, description=description)
        msg = click.style(
            f"✅ Plugin '{name}' initialized successfully.", fg="green", bold=True
        )
        click.echo(msg)
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
        raise click.Abort() from e


if __name__ == "__main__":
    main()
