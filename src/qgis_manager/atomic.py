"""Atomic text writes shared by metadata and TOML helpers."""

from __future__ import annotations

import os
from pathlib import Path


def write_text_atomic(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically.

    A temporary file is created next to the destination and moved over it with
    :func:`os.replace`, so a failure cannot leave a half-written file.

    Args:
        path: Destination file.
        text: Content to write as UTF-8.

    Raises:
        OSError: If the temporary file cannot be written or moved.
    """
    tmp_path = path.with_name(f".{path.name}.tmp")
    try:
        tmp_path.write_text(text, encoding="utf-8")
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)
