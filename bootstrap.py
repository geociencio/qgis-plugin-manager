#!/usr/bin/env python3
"""
Bootstrap script for Antigravity-powered projects.
Automates project name replacement and environment initialization.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, shell=True):
    """Run a shell command and return success."""
    try:
        subprocess.run(command, shell=shell, check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_environment():
    """Verify that the environment meets the minimum requirements."""
    print("🔍 Checking environment...")

    # 1. Python version check
    if sys.version_info < (3, 10):  # noqa: UP036
        print("  ❌ Error: Python 3.10+ is required.")
        return False
    print("  ✅ Python 3.10+")

    # 2. Check for uv
    if not run_command("uv --version"):
        print(
            "  ❌ Error: `uv` is not installed. Please install it: https://github.com/astral-sh/uv"
        )
        return False
    print("  ✅ uv found")

    return True


def setup_project():
    print("🚀 Antigravity Project Bootstrapper")
    print("-----------------------------------")

    if not check_environment():
        sys.exit(1)

    # Get project name
    project_name = input(
        "\nEnter the new project name (e.g., my-awesome-plugin): "
    ).strip()
    if not project_name:
        print("❌ Error: Project name cannot be empty.")
        sys.exit(1)

    # Files to process
    files_to_process = [
        Path("pyproject.toml"),
        Path("README.md"),
        Path(".agent/AGENTS.md"),
    ]

    # Placeholders
    placeholder_name = "{{PROJECT_NAME}}"
    placeholder_dir = "{{PROJECT_DIR}}"
    current_dir = str(Path.cwd().resolve())

    print(f"\n📝 Replacing placeholders in {len(files_to_process)} files...")

    for file_path in files_to_process:
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                updated = False

                # Replace Project Name
                if placeholder_name in content:
                    content = content.replace(placeholder_name, project_name)
                    updated = True

                # Replace Project Directory (for absolute paths in Agent Config)
                if placeholder_dir in content:
                    content = content.replace(placeholder_dir, current_dir)
                    updated = True

                if updated:
                    file_path.write_text(content, encoding="utf-8")
                    print(f"  ✅ Updated {file_path}")
                else:
                    print(f"  ⚠️  No placeholders found/updated in {file_path}")
            except Exception as e:
                print(f"  ❌ Error processing {file_path}: {e}")
        else:
            print(f"  ⚠️  File {file_path} not found.")

    # Initialize uv environment
    print("\n📦 Initializing environment with `uv sync`...")
    if run_command("uv sync"):
        print("  ✅ Environment initialized successfully.")
    else:
        print("  ❌ Error: Failed to run `uv sync`.")
        sys.exit(1)

    # Git Initialization
    print("\n🐙 Git Initialization...")
    if not Path(".git").exists():
        if run_command("git init"):
            print("  ✅ Git repository initialized.")
            if run_command("git add .") and run_command(
                'git commit -m "initial: project setup with Antigravity Framework"'
            ):
                print("  ✅ Initial commit created.")
    else:
        print("  ℹ️ Git repository already exists.")

    print("\n✨ Bootstrap complete! Your project is ready.")
    print("Next steps:")
    print("1. Explore AGENTS.md in scaffold/")
    print("2. Run `/inicia-sesion` to start collaborating with your agent.")

    # Self-destruct?
    delete_self = input(
        "\nDo you want to delete this bootstrap script? (y/N): "
    ).lower()
    if delete_self == "y":
        try:
            os.remove(__file__)
            print("  ✅ bootstrap.py removed.")
        except Exception as e:
            print(f"  ⚠️  Could not remove bootstrap.py: {e}")


if __name__ == "__main__":
    setup_project()
