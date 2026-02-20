# Release Notes - v0.6.4

**Fecha**: 2026-02-19

Esta actualización menor (`v0.6.4`) y la subversión previa (`0.6.4` integrada) se enfocan exclusivamente en blindar la arquitectura del core, el validador y el empaquetador de la herramienta, subsanando vulnerabilidades arquitectónicas durante el desarrollo local y el despliegue automático.

## 🚀 Mejoras Principales (Improvements)

- **Prevención de Symlinks**: `qgis-manage package` y los empaquetadores internos ya no colapsarán al encontrarse un symlink recursivo; estos son automáticamente evadidos.
- **Limpieza de Proyecto (Cache)**: `qgis-manage clean` ahora es más agresivo purgando directorios residuales del entorno de desarrollo como `.pytest_cache`, `.ruff_cache` ademá de los subproductos espaciales escondidos `*.qpj` y `*.cpg`.
- **Ignore Parser Exclusivo**: Si usas un `.qgisignore`, la herramienta ignorará categóricamente el `.gitignore`. Además, el parser ahora entiende de "Implicit Directory Recursion", logrando paridad completa con el comportamiento standard de Git.
- **QGIS Metadata SemVer**: Se ha flexibilizado la validación de versiones reemplazando la lógica simple por un parser oficial SemVer 2.0; esto significa que tu `metadata.txt` ahora puede usar tags de Pre-Releases como `1.0.0-beta.1` sin encender advertencias.

## 🐛 Fixes
- Line length and regex formatting issues en el código fuente (Ruff `E501`).
- `test_validation.py` fue actualizado para aceptar versiones beta.
