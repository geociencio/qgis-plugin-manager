"""Deploy command implementation."""

import argparse
from pathlib import Path

import click

from ...config import load_config, load_project_config
from ...core import compile_qt_resources, deploy_plugin, get_qgis_plugin_dir
from ...discovery import find_project_root, get_plugin_metadata
from ...hooks import run_hook
from ..base import BaseCommand


class DeployCommand(BaseCommand):
    """Command to deploy the plugin to a local QGIS profile."""

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

    def execute(self, args: argparse.Namespace) -> int:
        try:
            root = find_project_root(Path(args.path))

            # Load config
            settings = load_config()
            settings = load_project_config(root, settings)

            # Defaults
            target_profile = args.profile or settings.profile
            use_backup = not args.no_backup if args.no_backup else settings.backup

            # Pre-info
            metadata = get_plugin_metadata(root)
            slug = metadata["slug"]

            # Handle --purge-backups
            if args.purge_backups:
                target_dir = get_qgis_plugin_dir(target_profile)
                msg = (
                    f"🗑️  Purge all backups for '{slug}' "
                    f"in profile '{target_profile}'?"
                )
                if click.confirm(msg):
                    from ...core import rotate_backups

                    rotate_backups(target_dir, slug, limit=0)
                    click.echo("✨ Backups purged.")

                if not click.confirm("Proceed with deployment?"):
                    return 0

            # Destination determination
            if args.profile and Path(args.profile).is_absolute():
                target_path = Path(args.profile)
            else:
                target_dir = get_qgis_plugin_dir(target_profile)
                target_path = target_dir / slug

            # Pre-deploy hook
            pre_hook = settings.hooks.get("pre-deploy")
            # Build context for native hooks
            hook_ctx = {
                "project_root": root,
                "metadata": metadata,
                "profile": target_profile,
                "target_path": target_path,
                "args": vars(args),
            }

            if pre_hook or (root / "plugin_hooks.py").exists():
                if args.interactive:
                    if not click.confirm("🪝  Execute pre-deploy hook?"):
                        click.echo("⏭️  Skipping hook.")
                        pre_hook = None

                if not run_hook("pre-deploy", pre_hook, root, context=hook_ctx):
                    return 1

            if args.interactive:
                if not click.confirm(f"🚀 Deploy to profile '{target_profile}'?"):
                    click.echo("Aborted by user.")
                    return 1

            if not args.no_compile and settings.auto_compile:
                # Calculate steps: qrcs + ts + 1 (docs)
                qrc_count = len(list(root.rglob("*.qrc")))
                ts_count = len(list(root.rglob("*.ts")))
                has_docs = (root / "docs" / "source" / "conf.py").exists()
                total_steps = qrc_count + ts_count + (1 if has_docs else 0)

                if total_steps > 0:
                    with click.progressbar(
                        length=total_steps,
                        label="📚 Compiling resources and docs",
                        show_pos=True,
                    ) as bar:

                        def comp_callback(line):
                            import time

                            icons = {
                                "Recurso": "🔨",
                                "Trad": "🌍",
                                "Documentación": "📚",
                            }
                            msg = line.split(":", 1)[1] if ":" in line else line
                            short_msg = msg[:40] + "..." if len(msg) > 40 else msg

                            if line.startswith("START:"):
                                icon = "🛠️"
                                for k, v in icons.items():
                                    if k in msg:
                                        icon = v
                                        break
                                bar.label = f"{icon} {short_msg}"
                                bar.update(0)
                            elif line.startswith("PROGRESS:"):
                                spinner = [
                                    "⠋",
                                    "⠙",
                                    "⠹",
                                    "⠸",
                                    "⠼",
                                    "⠴",
                                    "⠦",
                                    "⠧",
                                    "⠇",
                                    "⠏",
                                ]
                                s = spinner[int(time.time() * 5) % len(spinner)]
                                bar.label = f"📚 {s} {short_msg}"
                                bar.update(0)
                            elif line.startswith("DONE:"):
                                bar.update(1)

                        compile_qt_resources(root, "all", callback=comp_callback)

            click.echo(f"🚀 Deploying '{metadata['name']}' ({slug}) to {target_path}")

            # Deployment
            deploy_plugin(
                root,
                no_backup=not use_backup,
                profile=target_profile,
                max_backups=settings.max_backups,
            )

            # Post-deploy hook
            post_hook = settings.hooks.get("post-deploy")
            if post_hook or (root / "plugin_hooks.py").exists():
                if args.interactive:
                    if not click.confirm("🪝  Execute post-deploy hook?"):
                        click.echo("⏭️  Skipping hook.")
                        post_hook = None

                run_hook("post-deploy", post_hook, root, context=hook_ctx)

            click.echo(click.style("✨ Deployment complete!", fg="green", bold=True))
            return 0

        except Exception as e:
            click.echo(click.style(f"❌ Error: {e}", fg="red", bold=True), err=True)
            return 1
