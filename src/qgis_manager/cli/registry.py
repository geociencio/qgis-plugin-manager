"""Ordered registry of CLI command classes."""

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
