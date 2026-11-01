"""Standard-library-only console helpers for the CLI.

This module replaces the small part of ``click`` that qgis-manage used:
colored output, prompts, confirmations and a lightweight progress bar.  The
public function names intentionally mirror the old calls so command code and
tests keep a familiar surface without a runtime dependency.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

_COLORS = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
}


def _color_enabled() -> bool:
    """Return whether ANSI styling should be emitted."""
    return (
        sys.stdout.isatty()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM") != "dumb"
    )


def style(text: str, fg: str | None = None, bold: bool = False) -> str:
    """Style ``text`` with ANSI codes when the terminal supports color."""
    if not _color_enabled():
        return text
    codes: list[str] = []
    if bold:
        codes.append("1")
    if fg and fg in _COLORS:
        codes.append(str(_COLORS[fg]))
    if not codes:
        return text
    return f"\033[{';'.join(codes)}m{text}\033[0m"


def echo(
    message: Any = "",
    *,
    err: bool = False,
    nl: bool = True,
    color: bool | None = None,
) -> None:
    """Write a message to stdout or stderr."""
    stream = sys.stderr if err else sys.stdout
    text = str(message)
    stream.write(text + ("\n" if nl else ""))
    stream.flush()


def confirm(prompt: str, default: bool = False) -> bool:
    """Ask a yes/no question; EOF aborts with ``False``."""
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        answer = input(f"{prompt}{suffix}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    if not answer:
        return default
    return answer in {"y", "yes"}


def prompt(text: str, default: str = "") -> str:
    """Ask for text input, falling back to ``default`` on empty/EOF."""
    suffix = f" [{default}] " if default else " "
    try:
        answer = input(f"{text}{suffix}").strip()
    except (EOFError, KeyboardInterrupt):
        return default
    return answer or default


class ProgressBar:
    """Minimal progress bar compatible with the old callback contract."""

    def __init__(self, length: int, label: str = "", show_pos: bool = True) -> None:
        self.length = max(int(length), 0)
        self.label = label
        self.show_pos = show_pos
        self._current = 0
        self._rendered = False

    @property
    def current(self) -> int:
        return self._current

    def update(self, amount: int) -> None:
        """Advance by ``amount`` and render when attached to a TTY."""
        self._current += max(int(amount), 0)
        if self._current > self.length:
            self._current = self.length
        if sys.stderr.isatty():
            self._render()

    def _render(self) -> None:
        total = self.length or 0
        position = f" ({self._current}/{total})" if self.show_pos else ""
        sys.stderr.write(f"\r{self.label}{position}")
        sys.stderr.flush()
        self._rendered = True

    def finish(self) -> None:
        if self._rendered:
            sys.stderr.write("\n")
            sys.stderr.flush()


@contextmanager
def progressbar(
    length: int,
    label: str = "",
    show_pos: bool = True,
    **_kwargs: Any,
) -> Iterator[ProgressBar]:
    """Context manager matching the progressbar API used by commands."""
    bar = ProgressBar(length, label=label, show_pos=show_pos)
    try:
        yield bar
    finally:
        bar.finish()
