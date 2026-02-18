"""CLI package for QGIS Plugin Manager."""

import sys

from .app import CLIApp


def main() -> None:
    """Main entry point for the QGIS Plugin Manager CLI."""
    app = CLIApp()
    sys.exit(app.run())


__all__ = ["CLIApp", "main"]
