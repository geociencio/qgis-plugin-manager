# Análisis técnico: qgis-manage 0.10.0

> **Fecha**: 2026-10-25
> **Versión analizada**: `qgis-manage` 0.10.0 (PyPI, 2026-10-25)
> **Entorno**: Linux (Manjaro), Python 3.12, proyecto `sec_interp` 3.11.0
> **Método**: lectura del código instalado (44 módulos, ~4.5k líneas) + mediciones
> reproducibles sobre este repositorio. Las cifras son locales (SSD) y sirven para
> comparar órdenes de magnitud, no como benchmark absoluto.
> **Documento histórico**: no forma parte de la documentación activa auditada por
> `scripts/check_docs.py`.

---

## 1. Resumen ejecutivo

`qgis-manage` 0.10.0 es una herramienta sólida en seguridad y correctitud de
metadatos: validación de slug, confinamiento de rutas, sync idempotente, edición
atómica de `metadata.txt`, compilación de docs atómica y gates de confianza para
hooks y dependencias. Sin embargo, el análisis y las mediciones revelan **tres
footguns que afectan al loop de desarrollo y al release**:

1. **Backups con resolución de un segundo**: dos `deploy` seguidos fallan con
   `File exists` (`rc=1`).
2. **`--type` no es repetible**: `--type resources --type translations` compila
   **solo** traducciones (last-wins de `argparse`), dejando `resources.py` obsoleto.
3. **`--release-version` no sincroniza `metadata.txt`**: el ZIP puede llamarse
   `X.Y.Z` y contener otra versión, que es la que valida el portal QGIS.

Además, `--repo-check` cuesta ~5.5× más que `package` porque recorre `.venv` y
`docs/` antes de aplicar `.qgisignore`, y `deploy` relee el contenido de todos los
archivos en cada sincronización.

---

## 2. Lo que 0.10.0 hace bien

- **Sync idempotente de deploy**: copia solo diferencias (tamaño + contenido),
  elimina lo que desaparece del origen y conserva entradas ignoradas del destino.
- **Endurecimiento**: `validate_slug` (ASCII, reservados de Windows), rechazo de
  symlinks, confinamiento del target a un hijo directo del directorio de plugins,
  ZIP con nombres POSIX y rechazo de versiones/`..`.
- **Metadatos atómicos**: `bump`, `sync` y `--stamp` actualizan claves dentro de
  `[general]` preservando comentarios, indentación y secciones; escritura atómica.
- **Docs atómicas**: Sphinx compila en un directorio temporal y solo reemplaza
  `help/html` si el build tuvo éxito (un fallo no borra la ayuda anterior).
- **Empaquetado determinista por defecto**: dos `package` consecutivos con las
  mismas fuentes producen el mismo SHA256 (verificado). `--stamp` rompe esa
  reproducibilidad a cambio de trazabilidad.
- **Exit codes útiles**: `compile` y el auto-compile de `deploy` salen ≠0 al fallar.
- **Trust gating**: hooks de proyecto y `install-deps`/dependencias de `package`
  requieren `--trust` explícito.

---

## 3. Mediciones

Tiempos con el binario del venv (`qgis-manage` directo) para aislar el arranque
de `uv`; 340 archivos desplegados, ZIP de 2.4 MB.

| Flujo | Tiempo | Nota |
| :--- | ---: | :--- |
| `--version` (baseline de arranque) | 88 ms | |
| `package` | 577 ms | |
| `package --repo-check` | **3 193 ms** | 5.5× por el escaneo de binarios |
| `deploy` sin cambios, con backup | 454 ms | ~335 ms comparando contenido |
| `deploy` sin cambios, `--no-backup` | 423 ms | backup de 11 MB ≈ 30 ms |
| `compile --type translations` (13 `.ts`), `--jobs 1` | 204 ms | |
| `compile --type translations` (13 `.ts`), `--jobs 4` | **132 ms** | −35 % |
| `deploy --purge-backups` sin TTY | **rc=1** | confirmación interactiva |

Superficie de escaneo del repositorio: **21 541 archivos** — 8 682 en `.venv`,
4 368 en `docs/`, 111 en `help/html`. El `rglob` de binarios de `--repo-check`
recorre ese árbol completo antes de filtrar con `.qgisignore`.

---

## 4. Hallazgos de riesgo (con reproducción)

### 4.1 Colisión de backups en el mismo segundo

`deploy_plugin` usa `datetime.now().strftime("%Y%m%d%H%M%S")`:

```text
📦 Creating backup at: sec_interp.bak.20261025090117
❌ Error: [Errno 17] File exists: '.../sec_interp.bak.20261025090117'
```

Dos deploys consecutivos dentro del mismo segundo fallan (`rc=1`). En un loop
guardar→deploy es frecuente. Workarounds: `--no-backup` o esperar 1 s. Fix
recomendado: microsegundos en el timestamp o `copytree(..., dirs_exist_ok=True)`
tras comprobar que el backup es de esta ejecución.

### 4.2 `--type` no es repetible

`--type` es un `argparse` simple (`dest="res_type"`); el último valor gana. El
comando que usa este repositorio:

```bash
qgis-manage compile --type resources --type translations
```

compila **solo** traducciones. Verificado en un proyecto temporal: se generaron
los 13 `.qm` y **no** se regeneró `resources.py`. Cualquier Makefile con esta
forma deja los recursos obsoletos silenciosamente.

### 4.3 `--release-version` no sincroniza `metadata.txt`

```bash
qgis-manage package --release-version 9.9.9
# ZIP: sec_interp.9.9.9.zip
unzip -p ... metadata.txt | grep ^version   # version=3.11.0
```

El nombre del ZIP y el contenido divergen; el portal QGIS valida el contenido.
Con `--stamp` (o `--sync-version`) sí coinciden. Recomendación: que `package`
avise/falla si `--release-version` ≠ versión de `metadata.txt` sin esos flags.

### 4.4 `--purge-backups` no es apto para CI

Pide dos `click.confirm` y no tiene `--yes`; con stdin cerrado devuelve `rc=1`.
`dclean` sí tiene `--yes`, así que la inconsistencia es de `deploy`.

### 4.5 `clean` puede borrar fuentes generadas versionadas

`_remove_compiled_outputs` elimina el `.py` hermano de cada `.qrc`/`.ui`. En este
repositorio eso es `resources/resources.py`, que está versionado y es necesario
para el empaquetado de CI. `make clean` lo borra; con 4.2, `make compile` **no**
lo regenera. Recomendación: `clean --dry-run` y/o no borrar archivos versionados
sin confirmación.

### 4.6 El parche manual de imports ya es redundante

0.10.0 auto-parchea las salidas de `rcc`/`uic` (`patch_resource_file`,
`patch_ui_file`). Verificado: compilación limpia en un directorio temporal produce
`from qgis.PyQt import QtCore` y cero líneas con `PyQt5`/`PySide`. El `sed` del
Makefile puede eliminarse.

---

## 5. Recomendaciones para el desarrollo de plugins QGIS

### 5.1 Release

1. **Versión consistente siempre**: en CI,
   `qgis-manage package --repo-check --stamp --release-version X.Y.Z`.
   `--stamp` inyecta `version`, `commitSha1`, `commitNumber`, `dateTime` y
   `experimental` (detecta `-rc/-beta`) solo en la copia empaquetada.
2. Si se prefiere reproducibilidad bit-a-bit, usar `--sync-version` y verificar
   con `git diff --exit-code metadata.txt` en lugar de `--stamp`.
3. `--repo-check` en CI/release, no en el loop local (5.5× aquí).
4. Comprobar frescura de `help/html` frente a `docs/source` antes de empaquetar:
   la herramienta no lo hace y un ZIP sin ayuda offline es un fallo de portal.

### 5.2 Loop de desarrollo

5. Compilar en invocaciones explícitas y en paralelo:

   ```bash
   qgis-manage compile --type resources --jobs 4
   qgis-manage compile --type translations --jobs 4
   ```

6. `deploy --no-compile --no-backup` para iterar; evitar el rebuild implícito de
   Sphinx (`auto_compile=true` por defecto) y la colisión de backups.
7. Configurar el proyecto para no depender de flags:

   ```toml
   [tool.qgis-manager]
   qgis_version = 4
   max_backups = 1
   auto_compile = false
   ```

8. Hooks solo para tareas ligeras (`plugin_hooks.py`, `--trust`, timeout 300 s,
   entorno mínimo sin `VIRTUAL_ENV`/`UV_CACHE_DIR`). Probar con
   `qgis-manage hooks test pre_deploy`.

### 5.3 Gates que la herramienta no cubre

9. `metadata.txt` ↔ `pyproject.toml`:
   `qgis-manage bump sync && git diff --exit-code metadata.txt`.
10. Whitelist del ZIP: verificar que no aparecen `tests/`, `.agent/`, `docs/`,
    `tools/` (SecInterp lo cumple: 340 archivos, 0 coincidencias).
11. `validate --strict --repo` como gate único de metadatos/licencia/binarios.
12. `analyze` no reenvía `--max-cc`; si el proyecto usa un umbral propio (10 en
    SecInterp), invocar `qgis-analyzer analyze . --max-cc 10` directamente.

---

## 6. Recomendaciones para qgis-manage (upstream)

| Prioridad | Mejora | Impacto esperado |
| :--- | :--- | :--- |
| **P0** | Timestamp de backup con microsegundos (o `dirs_exist_ok`) | elimina fallos de deploys consecutivos |
| **P0** | `--type` con `action="append"` o valor `"resources,translations"` | evita compilaciones incompletas silenciosas |
| **P0** | Error si `--release-version` ≠ versión de `metadata.txt` sin `--stamp`/`--sync-version` | evita publicar un ZIP con versión incoherente |
| **P0** | `deploy --purge-backups --yes` | CI y scripts no interactivos |
| **P0** | `clean --dry-run`; no borrar `.py` versionados sin aviso | evita pérdida de `resources.py` |
| **P1** | `_find_prohibited_binaries`: un solo `os.walk` podando `dirnames` con el matcher | `--repo-check` 3.2 s → <1 s; escala con el repo |
| **P1** | Manifiesto de deploy (ruta, tamaño, `mtime_ns`, hash) | ~335 ms → decenas de ms; lineal en plugins grandes |
| **P1** | Backup con reflink/hardlink cuando el FS lo permita | backup ≈ 0 coste en btrfs/xfs |
| **P1** | Staleness de `.qrc`/`.ts` y no reescribir salidas idénticas | árbol limpio tras `compile` |
| **P2** | `--json` en `validate/analyze/package`; `ignore check <path>`/`--explain` | depuración de `.qgisignore` (`fnmatch` ≠ gitignore) |
| **P2** | `analyze --max-cc N` passthrough | gates de CC reales |
| **P2** | `deploy --dry-run`, `profiles list`, `package --require-docs` | UX y seguridad de release |
| **P2** | `HookPolicy(shell=False)` por defecto | menor superficie de ejecución |

---

## 7. Acciones aplicadas en SecInterp

Como consecuencia de este análisis se corrigieron cuatro puntos del proyecto:

1. **Makefile**: `compile` ejecuta recursos y traducciones en invocaciones
   separadas con `--jobs`, y se eliminó el `sed` sobre `resources.py` (0.10.0 ya
   parchea los imports).
2. **Makefile `clean`**: rechaza ejecutarse si `resources/resources.py` tiene
   cambios locales y lo restaura tras `qgis-manage clean` (archivo versionado y
   necesario para el empaquetado de CI).
3. **CI de release**: el empaquetado usa `--repo-check --stamp` además de
   `--release-version`.
4. **`pyproject.toml`**: `[tool.qgis-manager]` fija `qgis_version = 4`,
   `max_backups = 1` y `auto_compile = false`.

---

## 8. Reproducción de las mediciones

```bash
# Tiempos (binario directo para aislar el arranque)
time .venv/bin/qgis-manage package -o /tmp/pkg
time .venv/bin/qgis-manage package -o /tmp/pkg --repo-check

# Deploy incremental
.venv/bin/qgis-manage deploy --no-compile --qgis-version 4 --profile /tmp/dep
.venv/bin/qgis-manage deploy --no-compile --qgis-version 4 --profile /tmp/dep

# Concurrencia de traducciones (13 catálogos)
.venv/bin/qgis-manage compile --type translations --jobs 1 /tmp/copy-j1
.venv/bin/qgis-manage compile --type translations --jobs 4 /tmp/copy-j4

# Incoherencia de versión
.venv/bin/qgis-manage package -o /tmp/p --release-version 9.9.9
unzip -p /tmp/p/sec_interp.9.9.9.zip sec_interp/metadata.txt | grep ^version
```

> **Nota**: los directorios temporales deben crearse en la misma invocación de
> shell en entornos con `/tmp` efímero por sesión.
