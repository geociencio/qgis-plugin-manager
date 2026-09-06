"""Custom argparse parser with a project-specific help layout.

Renders help following a fixed template:

    <prog> v<version>
    <description>

    Usage:
        <prog> [OPTIONS] <SUBCOMMAND>

    <groups...>

    Examples:
        ...

    <footer>
"""

import argparse
from typing import Any


class _HelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Preserves blank lines in descriptions and uses a ``Usage:`` prefix."""

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = "Usage: "
        return super()._format_usage(usage, actions, groups, prefix)


class HelpfulArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that renders a title before the usage section."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("formatter_class", _HelpFormatter)
        super().__init__(*args, **kwargs)
        self._title = ""

    def set_title(self, title: str) -> None:
        """Set the headline printed above the description."""
        self._title = title

    def format_help(self) -> str:
        formatter = self._get_formatter()

        header = self._title
        if self.description:
            header = f"{header}\n{self.description}" if header else self.description
        if header:
            formatter.add_text(header)

        formatter.add_usage(
            self.usage,
            self._actions,
            self._mutually_exclusive_groups,
            "Usage: ",
        )

        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        if self.epilog:
            formatter.add_text(self.epilog)

        return formatter.format_help()
