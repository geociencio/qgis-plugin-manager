"""Ordered registry of built-in and external CLI command classes."""

import logging
from importlib.metadata import entry_points

from .base import BaseCommand
from .commands.analyze import AnalyzeCommand
from .commands.bump import BumpCommand
from .commands.clean import CleanCommand
from .commands.compile import CompileCommand
from .commands.dclean import DCleanCommand
from .commands.deploy import DeployCommand
from .commands.hooks import HooksCommand
from .commands.init import InitCommand
from .commands.install_deps import InstallDepsCommand
from .commands.package import PackageCommand
from .commands.security import SecurityCommand
from .commands.validate import ValidateCommand

logger = logging.getLogger(__name__)

#: Registration order shown by ``qgis-manage --help``.
COMMAND_CLASSES: tuple[type[BaseCommand], ...] = (
    DeployCommand,
    DCleanCommand,
    CompileCommand,
    PackageCommand,
    InitCommand,
    CleanCommand,
    AnalyzeCommand,
    SecurityCommand,
    ValidateCommand,
    InstallDepsCommand,
    HooksCommand,
    BumpCommand,
)


def build_commands() -> tuple[BaseCommand, ...]:
    """Return built-in instances followed by external command entry points."""
    instances: list[BaseCommand] = [
        command_class() for command_class in COMMAND_CLASSES
    ]
    names = {command.name for command in instances}
    for entry in sorted(
        entry_points(group="qgis_manager.commands"), key=lambda e: e.name
    ):
        try:
            candidate = entry.load()
        except Exception as exc:  # noqa: BLE001 - third-party entry point boundary
            logger.error("Could not load command entry point %s: %s", entry.name, exc)
            continue
        if not isinstance(candidate, type) or not issubclass(candidate, BaseCommand):
            logger.error(
                "Entry point %s is not a BaseCommand subclass; skipping", entry.name
            )
            continue
        command = candidate()
        if command.name in names:
            raise ValueError(f"Duplicate command name from entry point: {command.name}")
        instances.append(command)
        names.add(command.name)
    return tuple(instances)
