"""Minimal ``{{ variable }}`` template rendering using only the standard library."""

import re
from pathlib import Path

_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render(text: str, **context: str) -> str:
    """Replace ``{{ var }}`` placeholders in ``text`` with values from ``context``.

    Unknown placeholders are left untouched.
    """
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        return str(context[key]) if key in context else match.group(0)

    return _PLACEHOLDER.sub(_replace, text)


def render_template(template_path: Path, **context: str) -> str:
    """Read a template file and render it."""
    return render(template_path.read_text(encoding="utf-8"), **context)
