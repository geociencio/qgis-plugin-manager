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
Core functionality for QGIS plugin deployment and management.

This package provides functions to deploy QGIS plugins to local profiles,
compile Qt resources and translations, clean build artifacts and package
plugins. It handles cross-platform path detection for Linux, macOS, and
Windows.

The public API is re-exported here for backwards compatibility, so existing
``from qgis_manager.core import <name>`` imports keep working after the former
monolithic ``core.py`` was split into cohesive submodules.
"""

from __future__ import annotations

from .cleanup import clean_artifacts
from .compile import (
    compile_docs,
    compile_qt_resources,
    compile_ui_files,
    count_compile_steps,
    get_rcc_tool,
    get_uic_tool,
    patch_resource_file,
    patch_ui_file,
    verify_resource_patch,
)
from .deploy import (
    deploy_plugin,
    plan_deploy,
    purge_backups,
    rotate_backups,
    sync_directory,
    uninstall_plugin,
)
from .package import (
    create_plugin_package,
    get_git_info,
    is_prerelease,
    stamp_metadata_text,
)
from .platform import get_qgis_plugin_dir
from .scaffold import init_plugin_project

__all__ = [
    "clean_artifacts",
    "compile_docs",
    "compile_qt_resources",
    "compile_ui_files",
    "count_compile_steps",
    "create_plugin_package",
    "deploy_plugin",
    "plan_deploy",
    "get_git_info",
    "get_qgis_plugin_dir",
    "get_rcc_tool",
    "get_uic_tool",
    "init_plugin_project",
    "is_prerelease",
    "patch_resource_file",
    "patch_ui_file",
    "purge_backups",
    "rotate_backups",
    "stamp_metadata_text",
    "sync_directory",
    "uninstall_plugin",
    "verify_resource_patch",
]
