"""Deploy command implementation."""

import argparse
from pathlib import Path

import click

from ...config import load_config, load_project_config
from ...core import (
    compile_qt_resources,
    count_compile_steps,
    deploy_plugin,
    get_qgis_plugin_dir,
)
from ...discovery import find_project_root, get_plugin_metadata
from ...hooks import run_hook
from ..base import BaseCommand
from ..progress import make_compile_callback


class DeployCommand(BaseCommand):
    """Command to deploy the plugin to a local QGIS profile."""

    examples = (
        "    # Deploy to the default QGIS profile\n"
        "    qgis-manage deploy\n\n"
        "    # Deploy to a QGIS 4 profile\n"
        "    qgis-manage deploy --qgis-version 4\n\n"
        "    # Deploy without creating a backup\n"
        "    qgis-manage deploy --no-backup\n"
    )

    @property
    def name(self) -> str:
        return "deploy"

    @property
    def help(self) -> str:
        return "Deploy the plugin to the local QGIS profile"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.add_common_args(parser)
        parser.add_argument(
            "--no-backup",
            action="store_true",
            help="Skip backup of existing installation",
        )
        parser.add_argument(
            "-i",
            "--interactive",
            action="store_true",
            help="Ask for confirmation before each step",
        )
        parser.add_argument(
            "--no-compile",
            action="store_true",
            help="Skip automatic resource compilation",
        )
        parser.add_argument(
            "--purge-backups",
            action="store_true",
            help="Remove all existing backups for this plugin",
        )
        parser.add_argument(
            "--qgis-version",
            type=int,
            help="Major QGIS version (3 or 4)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))

            # Load config
            settings = load_config()
            settings = load_project_config(root, settings)

            # Defaults
            target_profile = args.profile or settings.profile
            qgis_version = args.qgis_version or settings.qgis_version
            use_backup = settings.backup if not args.no_backup else False

            # Pre-info
            metadata = get_plugin_metadata(root)
            slug = metadata["slug"]

            # Handle --purge-backups
            if args.purge_backups:
                target_dir = get_qgis_plugin_dir(target_profile, version=qgis_version)
                msg = (
                    f"🗑️  Purge all backups for '{slug}' in profile '{target_profile}'?"
                )
                if click.confirm(msg):
                    from ...core import rotate_backups

                    rotate_backups(target_dir, slug, limit=0)
                    click.echo("✨ Backups purged.")

                if not click.confirm("Proceed with deployment?"):
                    return 0

            # Destination determination
            if args.profile and Path(args.profile).is_absolute():
                target_dir = Path(args.profile)
            else:
                target_dir = get_qgis_plugin_dir(target_profile, version=qgis_version)

                # Interactive check for directory existence
                if not target_dir.exists():
                    click.echo(
                        click.style(
                            f"⚠️  Target directory does not exist: {target_dir}",
                            fg="yellow",
                        )
                    )
                    if not click.confirm("Do you want to create it?"):
                        manual_path = click.prompt(
                            "Please enter the absolute path to the plugins directory "
                            "(or press Enter to abort)",
                            default="",
                        )
                        if not manual_path:
                            click.echo("Aborted.")
                            return 1
                        target_dir = Path(manual_path)
                    else:
                        target_dir.mkdir(parents=True)

            target_path = target_dir / slug

            # Pre-deploy hook
            pre_hook = settings.hooks.get("pre_deploy")
            # Build context for native hooks
            hook_ctx = {
                "project_root": root,
                "metadata": metadata,
                "profile": target_profile,
                "qgis_version": qgis_version,
                "target_path": target_path,
                "args": vars(args),
            }

            if pre_hook or (root / "plugin_hooks.py").exists():
                if args.interactive:
                    if not click.confirm("🪝  Execute pre-deploy hook?"):
                        click.echo("⏭️  Skipping hook.")
                        pre_hook = None

                if not run_hook("pre_deploy", pre_hook, root, context=hook_ctx):
                    return 1

            if args.interactive:
                if not click.confirm(
                    f"🚀 Deploy to profile '{target_profile}' (QGIS {qgis_version})?"
                ):
                    click.echo("Aborted by user.")
                    return 1

            if not args.no_compile and settings.auto_compile:
                total_steps = count_compile_steps(root, "all")

                if total_steps > 0:
                    with click.progressbar(
                        length=total_steps,
                        label="📚 Compiling resources and docs",
                        show_pos=True,
                    ) as bar:
                        compile_qt_resources(
                            root, "all", callback=make_compile_callback(bar)
                        )

            click.echo(f"🚀 Deploying '{metadata['name']}' ({slug}) to {target_path}")

            # Deployment
            deploy_plugin(
                root,
                dest_dir=target_dir,
                no_backup=not use_backup,
                profile=target_profile,
                qgis_version=qgis_version,
                max_backups=settings.max_backups,
            )

            # Post-deploy hook
            post_hook = settings.hooks.get("post_deploy")
            if post_hook or (root / "plugin_hooks.py").exists():
                if args.interactive:
                    if not click.confirm("🪝  Execute post-deploy hook?"):
                        click.echo("⏭️  Skipping hook.")
                        post_hook = None

                run_hook("post_deploy", post_hook, root, context=hook_ctx)

            click.echo(click.style("✨ Deployment complete!", fg="green", bold=True))
            return 0

        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
