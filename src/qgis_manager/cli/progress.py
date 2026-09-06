"""Shared progress-bar helpers for CLI commands."""

import time
from collections.abc import Callable

COMPILE_ICONS = {
    "Resource": "🔨",
    "Translation": "🌍",
    "Documentation": "📚",
}
_SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def make_compile_callback(bar) -> Callable[[str], None]:
    """Build a callback that drives a click progressbar from compile events.

    Args:
        bar: A click.progressbar instance.

    Returns:
        A callback accepting a single status line, formatted as
        ``START:...``, ``PROGRESS:...`` or ``DONE:...``.
    """

    def callback(line: str) -> None:
        msg = line.split(":", 1)[1] if ":" in line else line
        short_msg = msg[:40] + "..." if len(msg) > 40 else msg

        if line.startswith("START:"):
            icon = "🛠️"
            for key, value in COMPILE_ICONS.items():
                if key in msg:
                    icon = value
                    break
            bar.label = f"{icon} {short_msg}"
            bar.update(0)
        elif line.startswith("PROGRESS:"):
            symbol = _SPINNER[int(time.time() * 5) % len(_SPINNER)]
            bar.label = f"📚 {symbol} {short_msg}"
            bar.update(0)
        elif line.startswith("DONE:"):
            bar.update(1)

    return callback
