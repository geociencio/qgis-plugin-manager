"""Validation of built plugin ZIP artifacts."""

from __future__ import annotations

import configparser
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .fields import validate_version

_MAX_SIZE_MB = 25.0
_PROHIBITED_BINARIES = (".so", ".dll", ".exe", ".dylib", ".pyd", ".pyc", ".pyo")
_DEV_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "docs",
    "scripts",
    "test",
    "tests",
    "venv",
}
_CONFIG_FILES = {".bandit", ".flake8", ".secrets.baseline"}
_REQUIRED_FIELDS = (
    "name",
    "description",
    "about",
    "version",
    "qgisMinimumVersion",
    "author",
    "email",
    "repository",
)
_ROOT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


class ArtifactError(ValueError):
    """Raised when the input is not a readable ZIP artifact."""


@dataclass(frozen=True)
class ArtifactCheck:
    """One stable artifact validation finding."""

    id: str
    status: str
    message: str
    blocking: bool


@dataclass
class ArtifactResult:
    """Artifact validation result with stable check IDs."""

    path: Path
    root: str | None
    checks: list[ArtifactCheck] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def add(self, check_id: str, status: str, message: str) -> None:
        """Append a check and mirror it into errors/warnings."""
        blocking = status == "error"
        self.checks.append(ArtifactCheck(check_id, status, message, blocking))
        if blocking:
            self.errors.append(f"{check_id}: {message}")
        elif status == "warning":
            self.warnings.append(f"{check_id}: {message}")

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "path": str(self.path),
            "root": self.root,
            "checks": [
                {
                    "id": check.id,
                    "status": check.status,
                    "message": check.message,
                    "blocking": check.blocking,
                }
                for check in self.checks
            ],
        }


def _read_metadata(zf: zipfile.ZipFile, root: str) -> dict[str, str] | None:
    try:
        raw = zf.read(f"{root}/metadata.txt")
        text = raw.decode("utf-8")
    except (KeyError, UnicodeDecodeError):
        return None
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str  # type: ignore[method-assign, assignment]
    try:
        parser.read_string(text)
        return dict(parser["general"])
    except (configparser.Error, KeyError):
        return None


def _check_structure(result: ArtifactResult, names: list[str]) -> str | None:
    roots: set[str] = set()
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            result.add("ARTIFACT_ROOT", "error", f"Unsafe ZIP member: {name}")
            return None
        if path.parts:
            roots.add(path.parts[0])
    if len(roots) != 1:
        result.add(
            "ARTIFACT_ROOT",
            "error",
            f"ZIP must contain exactly one top-level folder; found {sorted(roots)}",
        )
        return None
    root = next(iter(roots))
    if not _ROOT_RE.match(root):
        result.add("ARTIFACT_ROOT", "error", f"Invalid plugin root: {root}")
        return None
    return root


def _check_metadata(
    result: ArtifactResult, zf: zipfile.ZipFile, root: str, zip_path: Path
) -> dict[str, str] | None:
    metadata = _read_metadata(zf, root)
    if metadata is None:
        result.add("ARTIFACT_METADATA", "error", "metadata.txt is missing or invalid")
        return None
    missing = [field for field in _REQUIRED_FIELDS if not metadata.get(field)]
    if missing:
        result.add(
            "ARTIFACT_METADATA",
            "error",
            f"Missing required metadata fields: {', '.join(missing)}",
        )
    version = metadata.get("version", "")
    if not validate_version(version, allow_short=False):
        result.add("ARTIFACT_METADATA", "error", f"Invalid version: {version!r}")
    prefix = f"{root}."
    stem = zip_path.stem
    if not stem.startswith(prefix):
        result.add(
            "ARTIFACT_METADATA",
            "error",
            f"ZIP filename does not start with '{prefix}'",
        )
    elif stem[len(prefix) :] != version:
        result.add(
            "ARTIFACT_METADATA",
            "error",
            f"ZIP filename version '{stem[len(prefix) :]}' != metadata '{version}'",
        )
    if metadata.get("qgisMinimumVersion") and not validate_version(
        metadata["qgisMinimumVersion"]
    ):
        result.add("ARTIFACT_METADATA", "error", "Invalid qgisMinimumVersion")
    return metadata


def _check_license(result: ArtifactResult, zf: zipfile.ZipFile, root: str) -> None:
    name = f"{root}/LICENSE"
    try:
        size = len(zf.read(name))
    except KeyError:
        result.add("ARTIFACT_LICENSE", "error", "LICENSE is missing")
        return
    if size == 0:
        result.add("ARTIFACT_LICENSE", "error", "LICENSE is empty")


def _check_content(result: ArtifactResult, names: list[str], root: str) -> None:
    for name in names:
        relative = PurePosixPath(name)
        if relative.parts[:1] != (root,):
            continue
        suffix = relative.suffix.lower()
        if suffix in _PROHIBITED_BINARIES:
            result.add("ARTIFACT_BINARY", "error", f"Prohibited binary: {name}")
        if any(part in _DEV_DIRS for part in relative.parts[1:]):
            result.add("ARTIFACT_DEV_FILE", "error", f"Development file: {name}")
        if (
            any(part.startswith(".") for part in relative.parts[1:])
            and relative.name not in _CONFIG_FILES
        ):
            result.add("ARTIFACT_DEV_FILE", "error", f"Hidden file: {name}")


def _check_qgis4(result: ArtifactResult, metadata: dict[str, str] | None) -> None:
    if metadata is None:
        return
    maximum = metadata.get("qgisMaximumVersion")
    if not maximum:
        result.add(
            "ARTIFACT_QGIS4",
            "warning",
            "qgisMaximumVersion is missing; expected at least 4.0",
        )
    else:
        parts = maximum.split(".")
        try:
            if (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0) < (4, 0):
                result.add(
                    "ARTIFACT_QGIS4",
                    "warning",
                    f"qgisMaximumVersion is {maximum}; expected at least 4.0",
                )
        except ValueError:
            result.add("ARTIFACT_QGIS4", "warning", "Invalid qgisMaximumVersion")
    if metadata.get("supportsQt6"):
        result.add(
            "ARTIFACT_QGIS4",
            "warning",
            "supportsQt6 is deprecated for QGIS 4",
        )


def _check_config_files(result: ArtifactResult, names: list[str], root: str) -> None:
    found = [
        name
        for name in names
        if name in {f"{root}/{config}" for config in _CONFIG_FILES}
    ]
    if found:
        result.add(
            "ARTIFACT_CONFIG",
            "info",
            f"Validated (configured): {', '.join(found)}",
        )


def _check_permissions(
    result: ArtifactResult, zf: zipfile.ZipFile, strict: bool
) -> None:
    bad: list[str] = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        mode = (info.external_attr >> 16) & 0o777
        if mode not in (0o644, 0o755):
            bad.append(f"{info.filename} ({mode:o})")
    if bad:
        status = "error" if strict else "warning"
        result.add(
            "ARTIFACT_PERMISSIONS",
            status,
            f"{len(bad)} files use non-portal modes: {', '.join(bad[:5])}",
        )


def _check_icon(
    result: ArtifactResult,
    zf: zipfile.ZipFile,
    metadata: dict[str, str] | None,
    root: str,
    min_px: int,
) -> None:
    icon = (metadata or {}).get("icon", "icon.png")
    name = f"{root}/{icon}"
    try:
        data = zf.read(name)
    except KeyError:
        result.add("ARTIFACT_ICON", "warning", f"Icon is missing: {icon}")
        return
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        result.add("ARTIFACT_ICON", "warning", f"Icon is not a PNG: {icon}")
        return
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width < min_px or height < min_px:
        result.add(
            "ARTIFACT_ICON",
            "warning",
            f"Icon is {width}x{height}; expected at least {min_px}px",
        )


def _check_readme(result: ArtifactResult, names: list[str], root: str) -> None:
    prefix = f"{root}/README"
    if not any(name.startswith(prefix) and len(name) > len(prefix) for name in names):
        result.add("ARTIFACT_README", "warning", "README is missing")


def _check_size(result: ArtifactResult, zip_path: Path, max_size_mb: float) -> None:
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        result.add(
            "ARTIFACT_SIZE",
            "error",
            f"ZIP size {size_mb:.2f} MB exceeds {max_size_mb:.0f} MB",
        )


def validate_artifact(
    zip_path: Path,
    *,
    max_size_mb: float = _MAX_SIZE_MB,
    icon_min_px: int = 32,
    strict_permissions: bool = False,
) -> ArtifactResult:
    """Validate a built plugin ZIP without reading the source tree."""
    if not zip_path.is_file():
        raise ArtifactError(f"ZIP not found: {zip_path}")
    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile as exc:
        raise ArtifactError(f"Invalid ZIP: {zip_path}") from exc

    result = ArtifactResult(path=zip_path, root=None)
    with zf:
        names = [info.filename for info in zf.infolist()]
        result.root = _check_structure(result, names)
        _check_size(result, zip_path, max_size_mb)
        _check_permissions(result, zf, strict_permissions)
        if result.root:
            metadata = _check_metadata(result, zf, result.root, zip_path)
            _check_license(result, zf, result.root)
            _check_content(result, names, result.root)
            _check_icon(result, zf, metadata, result.root, icon_min_px)
            _check_readme(result, names, result.root)
            _check_qgis4(result, metadata)
            _check_config_files(result, names, result.root)
    return result
