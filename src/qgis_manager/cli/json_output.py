"""Machine-readable CLI output helper."""

import json
from typing import Any

import click


def emit_json(
    command: str,
    success: bool,
    *,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    data: dict[str, Any] | None = None,
) -> None:
    """Print a single versioned JSON object on stdout."""
    click.echo(
        json.dumps(
            {
                "schema": 1,
                "command": command,
                "success": success,
                "errors": errors or [],
                "warnings": warnings or [],
                "data": data or {},
            }
        )
    )
