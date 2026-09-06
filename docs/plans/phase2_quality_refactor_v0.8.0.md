# Fase 2 — Refactorización de calidad (v0.8.0)

## 2.1 Centralizar TOML + sync de versión

Nuevo `src/qgis_manager/toml_utils.py` con:

- `load_toml(path) -> dict`
- `get_project_version(pyproject) -> str | None`
- `set_project_version(pyproject, version) -> bool` (carga/dump TOML, sin regex)
- `sync_metadata_version(root) -> str | None`

Refactorizar consumidores:

- `bump.py` `_get_pyproject_version` / `_update_version_in_files` → elimina el regex frágil con `re.DOTALL`.
- `package.py:47-63` (`--sync-version`) → reusar `sync_metadata_version`.
- `config.py`, `dependencies.py`, `ignore.py` → usar `load_toml`.

## 2.2 Extraer callback de progressbar duplicado

`compile.py:52-73` y `deploy.py:158-195` son idénticos → extraer a helper compartido
(p. ej. `cli/_progress.py` o método en `base.py`).

## 2.3 `get_rcc_tool` con verificación real

`core.py:260-271` → devolver herramienta solo si `subprocess.run(...).returncode == 0`;
si no, probar la siguiente de la lista.

## 2.4 Unificar convención de hooks (guion bajo)

- `deploy.py:117,210` → usar claves `"pre_deploy"` / `"post_deploy"` (con guion bajo),
  coherente con `plugin_hooks.py`, `hooks.py` (`_hooks_list` usa `pre_deploy`) y el README.
- `run_hook` (`hooks.py:31`) ya normaliza `-`→`_` para hooks nativos; mantener y documentar.

## 2.5 `package --repo-check` más completo

`package.py:66-87` → añadir `validate_project_structure(root, metadata)` para paridad con
`validate.py`, no solo `validate_metadata` + `validate_official_compliance`.

## 2.6 Robustecer test suite (pytest)

- Añadir `pytest` a `[dependency-groups] dev`.
- Añadir en `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- Verificar que corren tanto `python -m unittest discover tests` como `pytest`
  (los `unittest.TestCase` son compatibles con pytest).

## 2.7 Mejoras menores de mantenibilidad

- `deploy.py:143-195` y `compile.py:38-75`: deduplicar cálculo de `total_steps` y callback
  (se solapa con 2.2).
- Extraer constantes mágicas repetidas (listas de `icons`, `spinner`) a `constants.py`.

## Verificación

```bash
uv run ruff check .
uv run mypy .
uv run python -m unittest discover tests
uv run pytest
uv run qgis-manage deploy --help
uv run qgis-manage package --help
uv run qgis-manage bump --help
uv run qgis-manage validate --help
```
