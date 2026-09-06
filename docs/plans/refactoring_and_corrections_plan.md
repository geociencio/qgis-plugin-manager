# Plan de Refactorización y Corrección — `qgis-plugin-manager`

Plan maestro en tres fases para corregir bugs, mejorar la calidad del código
y limpiar el repositorio. Cada fase tiene su propio documento detallado:

- [Fase 1 — Correcciones de bugs (v0.7.1)](phase1_bugfixes_v0.7.1.md)
- [Fase 2 — Refactorización de calidad (v0.8.0)](phase2_quality_refactor_v0.8.0.md)
- [Fase 3 — Limpieza de repositorio](phase3_repo_cleanup.md)

## Resumen de prioridades

| Fase | Objetivo | Riesgo | Release |
| :--- | :--- | :--- | :--- |
| 1 | Corregir bugs y código muerto | Bajo | v0.7.1 (patch) |
| 2 | Refactorizar calidad y robustecer tests | Medio | v0.8.0 (minor) |
| 3 | Limpiar artefactos y documentar | Bajo | n/a |

## Decisiones tomadas

1. **Python 3.10** → subir `requires-python` a `>=3.11` (usar `tomllib` de stdlib, sin `tomli`).
2. **Imports de tests** → unificar a `from qgis_manager...` (sin prefijo `src.`).
3. **Alcance de esta iteración** → Fase 1 (bugs); Fases 2 y 3 quedan planificadas para después.
4. **Estrategia de release** → v0.7.1 (solo bugs) y v0.8.0 (refactor), sin mezclar ambos.

## Contexto del análisis

- `ruff check` y `mypy` pasan actualmente (0 issues en 23 archivos).
- Tests: 73 OK vía `python -m unittest discover tests` (el runner oficial del `Makefile`).
- Bug crítico: la ruta personalizada/interactiva de `deploy` se calcula pero nunca se pasa a
  `deploy_plugin()`, así que se ignora (feature ya anunciada en el CHANGELOG 0.7.0).
