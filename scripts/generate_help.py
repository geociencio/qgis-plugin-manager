"""Generate CLI help documentation into the ``help/`` directory.

Walks the argparse parser tree (main command, subcommands, and nested
sub-subcommands) and writes one Markdown file per command. Nested
sub-subcommands are folded into their parent command file.

Usage:
    uv run python scripts/generate_help.py
"""

import argparse
from pathlib import Path

from qgis_manager.cli.app import CLIApp

HELP_DIR = Path(__file__).resolve().parent.parent / "help"

# Commands with nested sub-subcommands. Keys are command names, values are
# the order in which sub-subcommands are rendered.
_NESTED = {"bump", "hooks"}


def _subparsers_action(parser: argparse.ArgumentParser) -> argparse.Action | None:
    for action in parser._actions:  # noqa: SLF001
        if action.__class__.__name__ == "_SubParsersAction":
            return action
    return None


def _render(parser: argparse.ArgumentParser, title: str) -> str:
    """Render a parser's help as a Markdown section."""
    help_text = parser.format_help().rstrip()
    return f"# {title}\n\n```text\n{help_text}\n```\n"


def _generate_command(
    parser: argparse.ArgumentParser, name: str, help_dir: Path
) -> None:
    """Write the Markdown help file for a command and its sub-subcommands."""
    subparsers = _subparsers_action(parser)
    sections = [_render(parser, f"qgis-manage {name}")]

    if subparsers is not None:
        for sub_name, sub_parser in subparsers.choices.items():
            sub_parser.prog = f"qgis-manage {name} {sub_name}"
            sub_parser._positionals.title = "Arguments"  # noqa: SLF001
            sub_parser._optionals.title = "Options"  # noqa: SLF001
            sections.append(_render(sub_parser, f"qgis-manage {name} {sub_name}"))

    (help_dir / f"{name}.md").write_text("\n".join(sections), encoding="utf-8")


def main() -> None:
    help_dir = HELP_DIR
    help_dir.mkdir(parents=True, exist_ok=True)

    app = CLIApp()
    root_parser = app._build_parser()  # noqa: SLF001

    # Main help
    (help_dir / "index.md").write_text(
        _render(root_parser, "qgis-manage"), encoding="utf-8"
    )

    main_subparsers = _subparsers_action(root_parser)
    if main_subparsers is None:
        raise RuntimeError("No subcommands found in the main parser")

    for name, command_parser in sorted(main_subparsers.choices.items()):
        _generate_command(command_parser, name, help_dir)

    print(f"Generated {len(main_subparsers.choices) + 1} help files in {help_dir}")


if __name__ == "__main__":
    main()
