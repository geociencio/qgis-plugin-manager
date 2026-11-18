"""Deploy command implementation."""

import argparse
from pathlib import Path
from typing import Any

from ...config import Settings, load_config, load_project_config
from ...core import (
    DeployPlan,
    DeployRequest,
    DeployWorkflow,
    compile_qt_resources,
    count_compile_steps,
    deploy_plugin,
    get_qgis_plugin_dir,
    plan_deploy,
)
from ...hooks import run_hook
from ...metadata import get_plugin_metadata
from .. import console
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
            "--no-manifest",
            action="store_true",
            help="Disable the content manifest and re-hash every file",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be copied, deleted, backed up or purged",
        )
        parser.add_argument(
            "--purge-backups",
            action="store_true",
            help="Remove all existing backups for this plugin",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Assume yes for purge/create/deploy confirmations",
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
        if args.interactive and args.yes:
            console.echo(
                "❌ --interactive and --yes cannot be used together.", err=True
            )
            return 1
        root = self.project_root(args)
        settings = load_project_config(root, load_config())
        target_profile = args.profile or settings.profile
        qgis_version = args.qgis_version or settings.qgis_version
        use_backup = settings.backup and not args.no_backup
        target_dir, absolute_profile = self._determine_target_dir(
            args, target_profile, qgis_version
        )
        workflow = DeployWorkflow(
            metadata_reader=get_plugin_metadata,
            deploy=deploy_plugin,
        )
        plan = self._prepare_plan(
            workflow,
            root,
            target_dir,
            target_profile,
            qgis_version,
            use_backup,
            settings,
            args,
        )
        if args.dry_run:
            return self._dry_run(plan, settings, args)
        return self._execute_plan(workflow, plan, settings, args)

    def _execute_plan(
        self,
        workflow: DeployWorkflow,
        plan: DeployPlan,
        settings: Settings,
        args: argparse.Namespace,
    ) -> int:
        target_dir = plan.request.target_dir
        target_profile = plan.request.profile
        if args.purge_backups and not self._purge_backups(
            target_dir, plan.slug, target_profile, args.yes
        ):
            return 0
        resolved = self._ensure_target_dir(
            target_dir,
            bool(args.profile and Path(args.profile).is_absolute()),
            args.yes,
        )
        if resolved is None:
            return 1
        if resolved != target_dir:
            plan = self._prepare_plan(
                workflow,
                plan.request.project_root,
                resolved,
                target_profile,
                plan.request.qgis_version,
                plan.request.backup,
                settings,
                args,
            )
        hook_ctx = self._hook_context(plan, args)
        if not self._run_hook(
            "pre_deploy",
            settings.hooks.get("pre_deploy"),
            plan.request.project_root,
            hook_ctx,
            args,
            required=True,
        ):
            return 1
        if args.interactive and not console.confirm(
            f"🚀 Deploy to profile '{target_profile}' "
            f"(QGIS {plan.request.qgis_version})?"
        ):
            console.echo("Aborted by user.")
            return 1
        if not self._compile_if_needed(plan.request.project_root, args, settings):
            return 1
        console.echo(
            f"🚀 Deploying '{plan.metadata['name']}' ({plan.slug}) to "
            f"{plan.target_path}"
        )
        workflow.execute(plan)
        self._run_hook(
            "post_deploy",
            settings.hooks.get("post_deploy"),
            plan.request.project_root,
            hook_ctx,
            args,
            required=False,
        )
        console.echo(console.style("✨ Deployment complete!", fg="green", bold=True))
        return 0

    @staticmethod
    def _prepare_plan(
        workflow: DeployWorkflow,
        root: Path,
        target_dir: Path,
        profile: str,
        qgis_version: int,
        backup: bool,
        settings: Settings,
        args: argparse.Namespace,
    ) -> DeployPlan:
        return workflow.prepare(
            DeployRequest(
                project_root=root,
                target_dir=target_dir,
                profile=profile,
                qgis_version=qgis_version,
                backup=backup,
                max_backups=settings.max_backups,
                use_manifest=not args.no_manifest,
            )
        )

    def _determine_target_dir(
        self, args: argparse.Namespace, profile: str, qgis_version: int
    ) -> tuple[Path, bool]:
        absolute_profile = bool(args.profile and Path(args.profile).is_absolute())
        if absolute_profile:
            return Path(args.profile), True
        return get_qgis_plugin_dir(profile, version=qgis_version), False

    def _dry_run(
        self,
        plan: DeployPlan,
        settings: Settings,
        args: argparse.Namespace,
    ) -> int:
        root = plan.request.project_root
        target_dir = plan.request.target_dir
        target_path = plan.target_path
        backups = (
            len(list(target_dir.glob(f"{plan.slug}.bak.*")))
            if target_dir.is_dir()
            else 0
        )
        counts = plan_deploy(root, target_path, no_backup=not settings.backup)
        console.echo(f"🧪 Dry run: {plan.slug} -> {target_path}")
        console.echo(f"  Files to copy: {counts['copy']}")
        console.echo(f"  Files to delete: {counts['delete']}")
        console.echo(f"  Backup: {'yes' if counts['backup'] else 'no'}")
        console.echo(f"  Existing backups: {backups}")
        if args.purge_backups:
            console.echo(f"  Backups to purge: {backups}")
        if settings.hooks.get("pre_deploy") or (root / "plugin_hooks.py").exists():
            message = (
                "would run only with --trust"
                if not args.trust
                else "would run (pre_deploy/post_deploy)"
            )
            console.echo(f"  Hooks: {message}")
        console.echo("  Manifest: would be updated after a successful deploy")
        return 0

    def _purge_backups(
        self, target_dir: Path, slug: str, profile: str, assume_yes: bool = False
    ) -> bool:
        msg = f"🗑️  Purge all backups for '{slug}' in profile '{profile}'?"
        if not assume_yes and not console.confirm(msg):
            return False
        from ...core import purge_backups

        removed = purge_backups(target_dir, slug)
        console.echo(f"✨ Backups purged ({removed}).")
        return True

    def _ensure_target_dir(
        self,
        target_dir: Path,
        absolute_profile: bool,
        assume_yes: bool = False,
    ) -> Path | None:
        if absolute_profile or target_dir.exists():
            return target_dir
        console.echo(
            console.style(
                f"⚠️  Target directory does not exist: {target_dir}", fg="yellow"
            )
        )
        if assume_yes or console.confirm("Do you want to create it?"):
            target_dir.mkdir(parents=True)
            return target_dir
        manual_path = console.prompt(
            "Please enter the absolute path to the plugins directory "
            "(or press Enter to abort)",
            default="",
        )
        if not manual_path:
            console.echo("Aborted.")
            return None
        return Path(manual_path)

    def _hook_context(
        self, plan: DeployPlan, args: argparse.Namespace
    ) -> dict[str, Any]:
        return {
            "project_root": plan.request.project_root,
            "metadata": plan.metadata,
            "profile": plan.request.profile,
            "qgis_version": plan.request.qgis_version,
            "target_path": plan.target_path,
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
            console.echo(
                f"⚠️  Skipping {name.replace('_', '-')} hooks: project is untrusted "
                "(pass --trust).",
                err=True,
            )
            return True
        if args.interactive and not console.confirm(f"🪝  Execute {name} hook?"):
            console.echo("⏭️  Skipping hook.")
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
        with console.progressbar(
            length=total_steps,
            label="📚 Compiling resources and docs",
            show_pos=True,
        ) as bar:
            compiled = compile_qt_resources(
                root, "all", callback=make_compile_callback(bar)
            )
        if compiled:
            return True
        console.echo(
            console.style(
                "❌ Compilation failed; aborting deployment.",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        return False
