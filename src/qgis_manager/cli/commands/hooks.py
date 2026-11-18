"""Hooks command implementation."""

import argparse
from pathlib import Path

from ...hooks import discover_python_hooks, execute_python_hook
from .. import console
from ..base import BaseCommand


class HooksCommand(BaseCommand):
    """Command to manage and test plugin hooks."""

    examples = (
        "    # List all defined hooks\n"
        "    qgis-manage hooks list\n\n"
        "    # Test the pre_deploy hook in isolation\n"
        "    qgis-manage hooks test pre_deploy\n"
    )

    @property
    def name(self) -> str:
        return "hooks"

    @property
    def help(self) -> str:
        return "Manage and test plugin hooks"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--path",
            default=".",
            help="Project directory path (default: current directory)",
        )
        subparsers = parser.add_subparsers(
            dest="subcommand", metavar="SUBCOMMAND", help="Hooks subcommand"
        )

        # List
        subparsers.add_parser("list", help="List all defined hooks")

        # Init
        subparsers.add_parser("init", help="Initialize a plugin_hooks.py template")

        # Test
        test_parser = subparsers.add_parser(
            "test", help="Test a specific hook in isolation"
        )
        test_parser.add_argument(
            "hook_name", help="Name of the hook to test (e.g., pre_deploy)"
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = self.project_root(args)

        if args.subcommand == "list":
            return self._hooks_list(root)
        elif args.subcommand == "init":
            return self._hooks_init(root)
        elif args.subcommand == "test":
            return self._hooks_test(root, args.hook_name)
        else:
            # If no subcommand, show help
            console.echo(
                console.style(
                    "❌ No subcommand specified. Use --help for usage.", fg="red"
                )
            )
            return 1

    def _hooks_list(self, root: Path) -> int:
        """List all discovered hooks."""
        console.echo(
            console.style(f"🔍 Scanning for hooks in {root.name}...", bold=True)
        )

        # 1. Inspect plugin_hooks.py without executing project code.
        py_hooks = discover_python_hooks(root)

        # 2. Check pyproject.toml
        from ...config import Settings, load_project_config

        config = load_project_config(root, Settings())
        toml_hooks = config.hooks

        if not py_hooks and not toml_hooks:
            console.echo("  (No hooks found)")
            return 0

        if py_hooks:
            console.echo(
                console.style(
                    "\n🐍 Native Python Hooks (plugin_hooks.py):", fg="blue", bold=True
                )
            )
            for h in py_hooks:
                console.echo(f"  • {h}")

        if toml_hooks:
            console.echo(
                console.style(
                    "\n📜 Configuration Hooks (pyproject.toml):",
                    fg="magenta",
                    bold=True,
                )
            )
            for h, cmd in toml_hooks.items():
                console.echo(f"  • {h}: {cmd}")

        return 0

    def _hooks_init(self, root: Path) -> int:
        """Initialize a plugin_hooks.py template."""
        hooks_file = root / "plugin_hooks.py"
        if hooks_file.exists():
            if not console.confirm(f"⚠️  {hooks_file.name} already exists. Overwrite?"):
                return 0

        template = '''"""
QGIS Plugin Hooks.

This file allows you to execute native Python code during different stages
of the plugin lifecycle.
"""

from typing import Any

def pre_deploy(context: dict[str, Any]):
    """Executed before the plugin is deployed to QGIS."""
    print(f"🪝 Pre-deploy hook running for {context.get('project_root')}")

def post_deploy(context: dict[str, Any]):
    """Executed after successful deployment."""
    print("🪝 Post-deploy hook finished.")

def pre_package(context: dict[str, Any]):
    """Executed before creating the distributable ZIP."""
    pass

def post_package(context: dict[str, Any]):
    """Executed after the ZIP is created."""
    pass
'''
        hooks_file.write_text(template, encoding="utf-8")
        console.echo(
            console.style(f"✅ Created {hooks_file.name} template.", fg="green")
        )
        return 0

    def _hooks_test(self, root: Path, hook_name: str) -> int:
        """Execute a hook in isolation with mock context."""
        console.echo(console.style(f"🧪 Testing hook: {hook_name}", bold=True))

        # Mock context
        context = {
            "project_root": root,
            "is_test": True,
            "plugin_id": root.name,
            "version": "test-mode",
        }

        success = execute_python_hook(root, hook_name, context)

        if success:
            console.echo(
                console.style(
                    f"✅ Hook '{hook_name}' executed successfully.", fg="green"
                )
            )
            return 0
        else:
            console.echo(
                console.style(f"❌ Hook '{hook_name}' failed or not found.", fg="red"),
                err=True,
            )
            return 1
