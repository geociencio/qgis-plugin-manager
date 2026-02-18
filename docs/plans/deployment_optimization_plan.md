# Implementation Plan: Phase 4 - Backup and Deployment Optimization

Improve the performance and safety of plugin deployments by introducing backup rotation, smart file synchronization, and cleanup utilities.

## Proposed Changes

### [Component Name] Configuration (src/qgis_manager/config.py)

#### [MODIFY] [config.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/config.py)
- Add `max_backups: int = 3` to `Settings` dataclass.
- Update `load_config` and `load_project_config` to read `max_backups`.

### [Component Name] Core Logic (src/qgis_manager/core.py)

#### [MODIFY] [core.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/core.py)
- **Implement `rotate_backups(parent_dir: Path, slug: str, limit: int)`**:
    - Discover files matching `{slug}.bak.*`.
    - Sort them by timestamp (newest first).
    - Remote those exceeding the `limit`.
- **Implement `sync_directory(src: Path, dst: Path, matcher: PathFilter)`**:
    - Recursively copy files from `src` to `dst`.
    - Use timestamp comparison to skip unchanged files.
    - Remove files in `dst` that are no longer in `src` (unless ignored).
- **Update `deploy_plugin`**:
    - Use `rotate_backups` before deployment.
    - Switch from `shutil.rmtree` + `shutil.copytree` to `sync_directory`.

### [Component Name] CLI (src/qgis_manager/cli/commands/deploy.py)

#### [MODIFY] [deploy.py](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/src/qgis_manager/cli/commands/deploy.py)
- Add `--purge-backups` flag to perform a full cleanup of old backups.

## Verification Plan

### Automated Tests
- Create `tests/test_deployment_optimization.py`:
    - Test `rotate_backups` with multiple dummy backup directories.
    - Test `sync_directory` to ensure only modified files are updated.

### Manual Verification
- Deploy a plugin multiple times and verify that only 3 backups (or the configured amount) remain.
- Run `qgis-manage deploy --purge-backups` and verify all backups are removed.
