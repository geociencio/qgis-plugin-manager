# Next Steps

**Fecha**: 2026-05-12
**Contexto**: Se ha completado la implementación del soporte multiversión (QGIS 3 y 4) y se ha lanzado la versión **v0.7.0**.

**Pendientes (What's missing):**
- [ ] **Validar las integraciones del CLI (Typer)** hacia las nuevas plantillas (blueprints) de `/scaffold`.
- [ ] **Resolver las deudas de `ruff` en la carpeta `scripts/`**. Se recomienda agregar `exclude = ["scripts/"]` en el `pyproject.toml` o corregir los errores E501/E741 manualmente.
- [ ] **Probar el despliegue interactivo en Windows y macOS** para confirmar que la creación de directorios funciona como se espera en entornos no-Linux.

**Comando para reanudar:**
`/start-session`
