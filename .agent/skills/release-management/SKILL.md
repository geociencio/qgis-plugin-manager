---
name: release-management
description: Estándares para el proceso de liberación de herramientas CLI con validación de calidad.
trigger: al preparar lanzamientos, actualizar versiones o usar el workflow /release-plugin
---

# Gestión de Releases (Herramientas CLI)

Controla el ciclo de vida de las versiones de la herramienta, garantizando que cada entrega cumpla con los estándares de calidad de PyPI y el proyecto.

## Cuándo usar este skill
- Al finalizar una fase de desarrollo y preparar una nueva versión.
- Al actualizar `pyproject.toml` o `metadata.txt`.
- Al generar notas de versión o actualizar el changelog.
- Al usar el workflow `/release-plugin`.

## Grado de Libertad
- **Estricto**: El proceso de 5 fases y los requisitos de calidad son innegociables.

## Workflow Detallado

### Fase 1: Calidad y Preparación
1. **Análisis de Calidad**:
   ```bash
   uv run ruff check . && uv run mypy src/
   ```
   - Validar: Cero errores de linting y tipado.
2. **Actualizar Badges**: Reflejar métricas en `README.md` (CI, PyPI status).

### Fase 2: Versionado y Documentación
1. **Sincronización**: Usar `qgis-manage bump` para actualizar versiones en `pyproject.toml` y `metadata.txt`.
2. **Reglas Semver**:
   - MAJOR (X): Cambios incompatibles.
   - MINOR (Y): Nuevas funcionalidades.
   - PATCH (Z): Correcciones.
3. **Notas de Versión**: Generar en `docs/releases/RELEASE_NOTES_vX.Y.Z.md`.

### Fase 3: Verificación Técnica
1. Lograr que el 100% de los tests pasen vía `uv run pytest`.
2. Verificar la integridad de la CLI con `uv run qgis-manage --help`.

### Fase 4: Git y Etiquetado
1. Commit de release: `chore(release): prepare vX.Y.Z`.
2. Etiqueta: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
3. Push: `git push origin main --tags`.

### Fase 5: Construcción y Distribución
1. Build: `uv build`.
2. Validar artefactos en `dist/`: `.whl` (Wheel) y `.tar.gz` (Source Distribution).
3. Carga: `uv publish` para subir a PyPI y crear release en GitHub.

## Checklist de Calidad
- [ ] ¿Pasa los chequeos de `ruff` y `mypy` al 100%?
- [ ] ¿Se ha usado `bump` para sincronizar versiones?
- [ ] ¿Se han generado los artefactos de build (`uv build`)?
- [ ] ¿Se han seguido las reglas de Git Tagging?
- [ ] ¿Todos los tests pasaron satisfactoriamente?
