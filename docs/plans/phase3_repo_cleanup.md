# Fase 3 — Limpieza de repositorio

## 3.1 Artefactos de desarrollo/AI en la raíz

Revisar `.gitignore` y `[tool.hatch.build.targets.sdist] exclude` para cubrir:

- `project_context.json`, `AI_CONTEXT.md`, `.ai_context_cache.json`, `.ai-context/`
- `analysis_results/`, `generator_export/`, `scaffold/`
- `bootstrap.py`, `agentic_framework_guide.md`, `agentic_framework_skeleton.zip`
- `test.bak.deploy` (0 bytes, vacío → eliminar)
- `metadata.txt` de raíz (artefacto de detección; documentar si es intencional)

## 3.2 Regenerar `dist/`

- `dist/` contiene artefactos `0.6.4`; regenerar wheel + sdist para `0.7.0`/`0.7.1`,
  o decidir no versionar `dist/` (verificar `dist/.gitignore`).

## 3.3 Bilingüismo

- Alinear docstrings/comentarios: `core.py:203-257` (`compile_docs` en español) y logs en español.
- Decidir política (inglés para docstrings; mensajes de usuario en inglés o ambos).

## 3.4 CI

- Verificar/actualizar `.github/workflows/main.yml` para que ejecute `ruff`, `mypy` y
  `unittest` (y `pytest` si se adopta en 2.6).

## 3.5 Documentación

- Actualizar `CHANGELOG.md` con entradas de v0.7.1 y v0.8.0.
- Actualizar `README.md` si cambia la convención de hooks o el soporte de Python.
