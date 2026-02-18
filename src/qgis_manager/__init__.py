# /***************************************************************************
#  QGIS Plugin Manager
#                                  A CLI Tool
#  Modern command-line interface for QGIS plugin development and deployment.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
QGIS Plugin Manager - A modern CLI tool for QGIS plugin development.

This package provides command-line utilities to deploy, compile, and manage
QGIS plugins across different platforms and profiles.
"""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Fallback for Python < 3.8 (though we require 3.10)
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("qgis-manage")
except PackageNotFoundError:
    # If package is not installed (e.g. during dev)
    __version__ = "0.0.0-unknown"

from .cli import main

if __name__ == "__main__":
    main()
