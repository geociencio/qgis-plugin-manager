---
description: Proceso unificado de liberación para herramientas CLI (PyPI Release Flow)
agent: QA Engineer
skills: [release-management, commit-standards, coding-standards]
validation: |
  - Verificar que todos los tests pasan localmente (uv run pytest)
  - Confirmar que ruff y mypy no reportan errores
  - Validar que las versiones están sincronizadas vía `qgis-manage bump sync`
  - Verificar que el build de PyPI (Wheel/Sdist) es correcto
---

Sigue este flujo de 5 fases para realizar una liberación oficial de la herramienta `qgis-manage`.

### Fase 1: Calidad y Preparación

🤖 **Agent Action**: Validar checklist completo de pre-release.

1. **Analizar Calidad**:
   // turbo
   ```bash
   uv run ruff check . && uv run mypy src/
   ```

   🤖 **Agent Action**: Verificar que no hay errores de linting ni de tipado estático (Type Hints).

2. **Actualizar Badges**: Asegurar que los badges de `Code Quality` y `PyPI` en `README.md` reflejen el estado actual.

### Fase 2: Versionamiento y Documentación

🤖 **Agent Action**: Usar `qgis-manage bump` para un versionado semántico impecable.

1. **Sincronizar Versión**:
   // turbo
   ```bash
   # Incrementar versión (elegir: patch, minor o major)
   uv run qgis-manage bump patch
   # Sincronizar metadata.txt (si se mantiene por compatibilidad)
   uv run qgis-manage bump sync
   ```

   🤖 **Agent Action**: Validar que `pyproject.toml` y `metadata.txt` tienen la misma versión.

2. **Changelog**: Actualizar `docs/releases/RELEASE_NOTES_vX.Y.Z.md` y el `CHANGELOG.md` principal.

### Fase 3: Verificación Técnica

1. **Linting Final**:
   // turbo
   ```bash
   uv run ruff check --fix . && uv run black .
   ```
2. **Tests**:
   // turbo
   ```bash
   uv run pytest
   ```

   🤖 **Agent Action**: Alertar si algún test falla o si hay regresión en la funcionalidad core.

### Fase 4: Git y Tagging

1. **Commit de Preparación**:
   ```bash
   git add pyproject.toml README.md docs/
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Fase 5: Compilación y Distribución (PyPI)

1. **Build**:
   // turbo
   ```bash
   uv build
   ```
   (Verificar archivos `.whl` y `.tar.gz` en `dist/`).

2. **Publicación**:
   ```bash
   uv publish
   ```

3. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md dist/* --draft
   ```

## Resultado Esperado
- Versión oficial disponible en PyPI (`pip install qgis-manage`).
- Tag de Git y Release de GitHub creados.
- Documentación técnica sincronizada con la nueva versión.
