# Fase 1 — Correcciones de bugs (v0.7.1)

## A. Subir a Python 3.11 y eliminar fallbacks TOML

1. `pyproject.toml`
   - `requires-python = ">=3.11"`
   - Quitar classifier `Programming Language :: Python :: 3.10`
   - `[tool.ruff] target-version = "py311"`
   - `[tool.mypy] python_version = "3.11"`
2. `src/qgis_manager/config.py:5-8` → eliminar rama `tomli`, usar `import tomllib`.
3. `src/qgis_manager/dependencies.py:6-9` → ídem.
4. `src/qgis_manager/ignore.py:31-64` y `114-117` → eliminar `TomlLoaderShim` y rama
   `sys.version_info`; `import tomllib` al inicio.
5. `src/qgis_manager/cli/commands/bump.py:180` → mover `import tomllib` al inicio del módulo.

## B. Bug de deploy con custom path

6. `src/qgis_manager/cli/commands/deploy.py:201-207` → pasar `dest_dir=target_path` a
   `deploy_plugin()` para que respete la ruta manual/interactiva (hoy se ignora y se
   recalcula con `get_qgis_plugin_dir`).

## C. Código muerto / redundante

7. `src/qgis_manager/core.py:271` → eliminar `return False` inalcanzable en `get_rcc_tool`.
8. `src/qgis_manager/core.py:190` → `except (ValueError, Exception)` → `except Exception`.
9. `src/qgis_manager/cli/app.py:96-100` → simplificar mapeo de `verbose` (ambos niveles dan DEBUG).
10. `src/qgis_manager/cli/commands/deploy.py:66` → `use_backup = settings.backup if not args.no_backup else False`.
11. `src/qgis_manager/config.py:23-50` → corregir docstring/comentario engañoso de `load_config()`
    (no lee `pyproject.toml`).

## D. Unificación de imports de tests

12. Cambiar `from src.qgis_manager` → `from qgis_manager` en:
    - `tests/test_hooks_native.py`
    - `tests/test_deployment_optimization.py`
    - `tests/test_ignore_system.py`
    - `tests/test_rcc_modernization.py`
    - `tests/test_validation_deep.py`

## Verificación

```bash
uv run ruff check .
uv run mypy .
uv run python -m unittest discover tests
uv run qgis-manage --help
uv run qgis-manage bump --help
uv run qgis-manage deploy --help
```
