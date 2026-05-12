# Guía de Mantenimiento y Evolución de qgis-manage para QGIS 4

Este documento detalla los cambios necesarios en la herramienta `qgis-manage` para eliminar hardcodes de versión (QGIS 3) y permitir un despliegue interactivo y flexible.

## 1. Problemas Identificados (Hardcodes)

Actualmente, `qgis-manage` tiene hardcodeada la versión 3 de QGIS en la detección de rutas:

```python
# qgis_manager/core.py
def get_qgis_plugin_dir(profile: str = "default") -> Path:
    if sys.platform == "linux":
        return Path.home() / f".local/share/QGIS/QGIS3/profiles/{profile}/python/plugins"
```

## 2. Cambios Propuestos en el Código Fuente

Para corregir esto, se deben realizar las siguientes modificaciones en el paquete `qgis-manage`:

### A. Soporte Multi-Versión en `core.py`
Modificar `get_qgis_plugin_dir` para aceptar un parámetro de versión:

```python
def get_qgis_plugin_dir(profile: str = "default", version: int = 3) -> Path:
    """Detecta el directorio de plugins basándose en la versión mayor de QGIS."""
    if sys.platform == "linux":
        return Path.home() / f".local/share/QGIS/QGIS{version}/profiles/{profile}/python/plugins"
    # Aplicar lógica similar para Windows (AppData) y macOS
```

### B. Nuevos Argumentos en `deploy.py`
Añadir el argumento `--qgis-version` al comando `deploy`:

```python
# qgis_manager/cli/commands/deploy.py
def configure_parser(self, parser: argparse.ArgumentParser) -> None:
    # ... otros argumentos ...
    parser.add_argument(
        "--qgis-version",
        type=int,
        default=3,
        help="Versión mayor de QGIS (3 o 4)",
    )
```

### C. Despliegue Interactivo de Rutas
Si el perfil no existe, `qgis-manage` debería preguntar interactivamente si se desea crear o buscar otra ubicación, en lugar de fallar o usar una ruta errónea.

## 3. Workaround Actual (Sin modificar qgis-manage)

Mientras no se actualice la herramienta `qgis-manage` globalmente, los desarrolladores deben usar el siguiente patrón en sus `Makefile`:

```makefile
# Makefile de SecInterp
QGIS_VERSION ?= 4
QGISDIR=.local/share/QGIS/QGIS$(QGIS_VERSION)/profiles/default
PLUGIN_DEPLOY_DIR=$(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

deploy:
    @# No usamos qgis-manage deploy directamente por el hardcode de QGIS3
    @# Usamos rsync para garantizar flexibilidad total
    rsync -av --delete --exclude-from=.qgisignore ./ $(PLUGIN_DEPLOY_DIR)/
```

## 4. Instrucciones para AI Agents

Cuando trabajes en la migración a QGIS 4:
1. **No confíes en `qgis-manage deploy`** por defecto si detectas un entorno QGIS 4.
2. **Verifica siempre la ruta de destino** antes de sincronizar.
3. **Usa `rsync`** como método de despliegue preferido si la herramienta de gestión tiene hardcodes de versión.
4. **Aplica parches de compatibilidad Qt6** en un archivo `qt6_compat.py` e impórtalo en el `sec_interp_plugin.py` para evitar errores de `AttributeError` en Enums movidos.

---
*Documentación generada para el equipo de desarrollo de SecInterp (Mayo 2026).*
