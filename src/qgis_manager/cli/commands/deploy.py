"""Deploy command implementation."""

import argparse
from pathlib import Path
from typing import Any

import click

from ...config import Settings, load_config, load_project_config
from ...core import (
    compile_qt_resources,
    count_compile_steps,
    deploy_plugin,
    get_qgis_plugin_dir,
)
from ...discovery import find_project_root, get_plugin_metadata, validate_slug
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
        parser.add_argument(
            "--trust",
            action="store_true",
            help="Allow hooks from this project to execute (trusted checkout only)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = find_project_root(Path(args.path))
        settings = load_project_config(root, load_config())

        target_profile = args.profile or settings.profile
        qgis_version = args.qgis_version or settings.qgis_version
        use_backup = settings.backup if not args.no_backup else False

        metadata = get_plugin_metadata(root)
        slug = validate_slug(str(metadata["slug"]), source="plugin metadata")

        target_dir, absolute_profile = self._determine_target_dir(
            args, target_profile, qgis_version
        )
        if args.purge_backups and not self._purge_backups(
            target_dir, slug, target_profile
        ):
            return 0

        resolved_target = self._ensure_target_dir(target_dir, absolute_profile)
        if resolved_target is None:
            return 1
        target_dir = resolved_target
        target_path = target_dir / slug

        hook_ctx = self._hook_context(
            root, metadata, target_profile, qgis_version, target_path, args
        )
        if not self._run_hook(
            "pre_deploy",
            settings.hooks.get("pre_deploy"),
            root,
            hook_ctx,
            args,
            required=True,
        ):
            return 1

        if args.interactive and not click.confirm(
            f"🚀 Deploy to profile '{target_profile}' (QGIS {qgis_version})?"
        ):
            click.echo("Aborted by user.")
            return 1

        if not self._compile_if_needed(root, args, settings):
            return 1

        click.echo(f"🚀 Deploying '{metadata['name']}' ({slug}) to {target_path}")
        deploy_plugin(
            root,
            dest_dir=target_dir,
            no_backup=not use_backup,
            profile=target_profile,
            qgis_version=qgis_version,
            max_backups=settings.max_backups,
        )

        self._run_hook(
            "post_deploy",
            settings.hooks.get("post_deploy"),
            root,
            hook_ctx,
            args,
            required=False,
        )
        click.echo(click.style("✨ Deployment complete!", fg="green", bold=True))
        return 0

    def _determine_target_dir(
        self, args: argparse.Namespace, profile: str, qgis_version: int
    ) -> tuple[Path, bool]:
        absolute_profile = bool(args.profile and Path(args.profile).is_absolute())
        if absolute_profile:
            return Path(args.profile), True
        return get_qgis_plugin_dir(profile, version=qgis_version), False

    def _purge_backups(self, target_dir: Path, slug: str, profile: str) -> bool:
        msg = f"🗑️  Purge all backups for '{slug}' in profile '{profile}'?"
        if click.confirm(msg):
            from ...core import purge_backups

            removed = purge_backups(target_dir, slug)
            click.echo(f"✨ Backups purged ({removed}).")
        return click.confirm("Proceed with deployment?")

    def _ensure_target_dir(
        self, target_dir: Path, absolute_profile: bool
    ) -> Path | None:
        if absolute_profile or target_dir.exists():
            return target_dir
        click.echo(
            click.style(
                f"⚠️  Target directory does not exist: {target_dir}", fg="yellow"
            )
        )
        if click.confirm("Do you want to create it?"):
            target_dir.mkdir(parents=True)
            return target_dir
        manual_path = click.prompt(
            "Please enter the absolute path to the plugins directory "
            "(or press Enter to abort)",
            default="",
        )
        if not manual_path:
            click.echo("Aborted.")
            return None
        return Path(manual_path)

    def _hook_context(
        self,
        root: Path,
        metadata: dict[str, Any],
        profile: str,
        qgis_version: int,
        target_path: Path,
        args: argparse.Namespace,
    ) -> dict[str, Any]:
        return {
            "project_root": root,
            "metadata": metadata,
            "profile": profile,
            "qgis_version": qgis_version,
            "target_path": target_path,
            "args": vars(args),
        }

    def _run_hook(
        self,
        name: str,
        command: str | None,
        root: Path,
        context: dict[str, Any],
        args: argparse.Namespace,
        *,
        required: bool,
    ) -> bool:
        if not (command or (root / "plugin_hooks.py").exists()):
            return True
        if not args.trust:
            click.echo(
                f"⚠️  Skipping {name.replace('_', '-')} hooks: project is untrusted "
                "(pass --trust).",
                err=True,
            )
            return True
        if args.interactive and not click.confirm(f"🪝  Execute {name} hook?"):
            click.echo("⏭️  Skipping hook.")
            command = None
        ok = run_hook(name, command, root, context=context)
        return ok if required else True

    def _compile_if_needed(
        self, root: Path, args: argparse.Namespace, settings: Settings
    ) -> bool:
        if args.no_compile or not settings.auto_compile:
            return True
        total_steps = count_compile_steps(root, "all")
        if total_steps <= 0:
            return True
        with click.progressbar(
            length=total_steps,
            label="📚 Compiling resources and docs",
            show_pos=True,
        ) as bar:
            compiled = compile_qt_resources(
                root, "all", callback=make_compile_callback(bar)
            )
        if compiled:
            return True
        click.echo(
            click.style(
                "❌ Compilation failed; aborting deployment.",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        return False
