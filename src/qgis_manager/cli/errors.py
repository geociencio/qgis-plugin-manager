"""Typed errors for expected CLI failures."""

from __future__ import annotations


class CliError(Exception):
    """An expected CLI error with a stable exit code."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code
