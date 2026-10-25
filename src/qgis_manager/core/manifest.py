"""Deployment manifest used to avoid re-reading unchanged files."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from ..metadata import write_text_atomic

logger = logging.getLogger(__name__)

_MANIFEST_VERSION = 1
_MANIFEST_DIR = ".qgis-manage"
_MANIFEST_NAME = "deploy-manifest.json"


def _sha256(path: Path) -> str:
    """Return the SHA256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stat_key(path: Path) -> tuple[int, int, int]:
    """Return size, mtime and ctime for change detection."""
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


class DeployManifest:
    """Per-project cache of content digests for one deployment target."""

    def __init__(self, project_root: Path, target_path: Path) -> None:
        self.project_root = project_root
        self.target_path = target_path
        self.path = project_root / _MANIFEST_DIR / _MANIFEST_NAME
        self._target_key = str(target_path.resolve())
        self.entries: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if data.get("version") != _MANIFEST_VERSION:
            return
        targets = data.get("targets")
        if not isinstance(targets, dict):
            return
        entries = targets.get(self._target_key)
        if isinstance(entries, dict):
            self.entries = {
                key: value for key, value in entries.items() if isinstance(value, dict)
            }

    def _source_key(self, src: Path) -> str | None:
        try:
            return src.relative_to(self.project_root).as_posix()
        except ValueError:
            return None

    def _matches(self, key: str, src: Path, dst: Path) -> bool:
        entry = self.entries.get(key)
        if not entry or not dst.is_file():
            return False
        try:
            source = _stat_key(src)
            target = _stat_key(dst)
        except OSError:
            return False
        return (
            entry.get("source_size") == source[0]
            and entry.get("source_mtime_ns") == source[1]
            and entry.get("source_ctime_ns") == source[2]
            and entry.get("target_size") == target[0]
            and entry.get("target_mtime_ns") == target[1]
            and entry.get("target_ctime_ns") == target[2]
            and bool(entry.get("source_sha256"))
            and bool(entry.get("target_sha256"))
        )

    def needs_copy(self, src: Path, dst: Path) -> bool:
        """Return True when the target differs, using cached digests when safe."""
        key = self._source_key(src)
        if key is None:
            return True
        if not dst.is_file():
            return True
        if self._matches(key, src, dst):
            return False
        entry = self.entries.get(key, {})
        try:
            source_stat = _stat_key(src)
            target_stat = _stat_key(dst)
        except OSError:
            return True
        source_hash = (
            entry.get("source_sha256")
            if entry.get("source_size") == source_stat[0]
            and entry.get("source_mtime_ns") == source_stat[1]
            and entry.get("source_ctime_ns") == source_stat[2]
            else _sha256(src)
        )
        target_hash = (
            entry.get("target_sha256")
            if entry.get("target_size") == target_stat[0]
            and entry.get("target_mtime_ns") == target_stat[1]
            and entry.get("target_ctime_ns") == target_stat[2]
            else _sha256(dst)
        )
        if source_hash == target_hash:
            self.record(src, dst, source_hash, target_hash)
            return False
        return True

    def record(
        self,
        src: Path,
        dst: Path,
        source_hash: str | None = None,
        target_hash: str | None = None,
    ) -> None:
        """Record current source/target fingerprints for a file."""
        key = self._source_key(src)
        if key is None or not dst.is_file():
            return
        try:
            source_stat = _stat_key(src)
            target_stat = _stat_key(dst)
        except OSError:
            return
        self.entries[key] = {
            "source_size": source_stat[0],
            "source_mtime_ns": source_stat[1],
            "source_ctime_ns": source_stat[2],
            "source_sha256": source_hash or _sha256(src),
            "target_size": target_stat[0],
            "target_mtime_ns": target_stat[1],
            "target_ctime_ns": target_stat[2],
            "target_sha256": target_hash or _sha256(dst),
        }

    def save(self) -> None:
        """Persist the manifest atomically; failures are non-fatal."""
        payload = {
            "version": _MANIFEST_VERSION,
            "targets": {self._target_key: self.entries},
        }
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            write_text_atomic(self.path, json.dumps(payload, indent=2) + "\n")
        except OSError as exc:
            logger.warning("Could not save deploy manifest: %s", exc)
