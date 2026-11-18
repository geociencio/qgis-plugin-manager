# Análisis manual de código — qgis-manage 0.16.1

**Fecha**: 2026-11-18
**Alcance**: código de producción en `src/qgis_manager` (~6.074 líneas, 50 módulos).
No se analizaron tests, documentación ni el repositorio del analyzer.
**Baseline**: 426 tests, 96.11 % statements, 90.33 % branches, 94.70 % combinado,
C901 = 0, cero dependencias runtime.
**Método**: lectura manual de los módulos, AST para funciones largas y búsqueda de
duplicaciones. No se modificó código durante el análisis.

## 1. Veredicto

La arquitectura general es buena: CLI fina, `core/` separado, validación aislada y
bajo acoplamiento externo. **C901 = 0 no significa ausencia de spaghetti**: la
complejidad se ha desplazado a orquestadores largos y a lógica duplicada de
recorrido de archivos.

Hay cinco problemas que deberían resolverse antes de añadir features; dos son de
seguridad.

## 2. Hallazgos críticos

### C1 — `hooks list` ejecuta `plugin_hooks.py` sin `--trust`

`src/qgis_manager/cli/commands/hooks.py` (`_hooks_list`, líneas 71-90) importa y
ejecuta `plugin_hooks.py` con `spec.loader.exec_module(module)` solo para listar
hooks. Cualquier repositorio no confiable ejecuta código al ejecutar
`qgis-manage hooks list`, contradiciendo el modelo de confianza de
`deploy --trust`.

**Recomendación**:

- analizar el AST de `plugin_hooks.py` para listar funciones sin ejecutarlo;
- compartir `discover_hooks(path, execute=False)` con `deploy`;
- test: un hook que escribe un marcador no debe ejecutarse con `hooks list`.

### C2 — `plan_deploy` no excluye el destino anidado

`src/qgis_manager/core/deploy.py` (`plan_deploy`, líneas 249-286) recorre el
proyecto sin el guard `_is_same_or_nested` que sí usa `sync_directory`. Si el
target está dentro del proyecto, el dry-run cuenta archivos del propio despliegue
y puede descender en copias anidadas.

**Recomendación**: aplicar el mismo guard que `sync_directory`; test con
`target_path` dentro de `project_root`.

### C3 — `compile_docs` puede borrar la documentación anterior

`src/qgis_manager/core/compile.py` (`compile_docs`, líneas 119-177) elimina
`help/html` antes de mover el nuevo build. Si `shutil.move` falla, la
documentación anterior ya no existe, pese a que el docstring promete lo
contrario.

**Recomendación**: staging + backup temporal + restauración en fallo, o
`os.replace` a nivel de directorio.

### C4 — `dclean --profile` no acepta ruta absoluta

`src/qgis_manager/cli/commands/dclean.py` (líneas 50-75) pasa el perfil
directamente a `uninstall_plugin`, que siempre construye
`get_qgis_plugin_dir(profile)`. `deploy` sí distingue perfiles absolutos.

**Recomendación**: extraer `resolve_profile_dir(profile, qgis_version)` y usarlo
en `deploy`, `dclean` y `profiles`; test con directorio absoluto temporal.

### C5 — Callbacks de compilación no son thread-safe

`src/qgis_manager/core/compile.py` (`_run_jobs`, líneas 360-372) ejecuta workers
en `ThreadPoolExecutor`; cada worker llama a `context.emit(...)`, que termina en
`console.ProgressBar.update` (`src/qgis_manager/cli/console.py`, líneas
102-115). El progress bar y la salida se mutan desde varios hilos con
`--jobs > 1`.

**Recomendación**: un único consumidor de eventos o un callback serializado con
lock/queue; test con `jobs=2` verificando orden y ausencia de intercalado.

## 3. Spaghetti y responsabilidades mezcladas

### S1 — `DeployCommand.execute` mezcla demasiadas decisiones

`src/qgis_manager/cli/commands/deploy.py` (líneas 92-174) hace validación de
flags, configuración, target, dry-run, purge, creación de directorio, hooks,
confirmación, compilación, deploy y post-hook.

Problemas concretos:

- `_purge_backups` devuelve `bool` pero además pregunta "Proceed with
  deployment?" y provoca un `return 0` desde `execute`;
- `_ensure_target_dir` mezcla creación, prompt y retorno de ruta;
- el flujo principal es una secuencia de `if not ... return`.

**Recomendación**: `DeployRequest` + `DeployWorkflow` en `core/deploy.py`:

```text
prepare(request) -> DeployPlan
confirm(plan) -> bool          # CLI
execute(plan) -> DeployResult  # core
render(result) -> None         # CLI
```

### S2 — `_build_package` duplica la llamada a `create_plugin_package`

`src/qgis_manager/cli/commands/package.py` (líneas 222-256) construye `options`
para el caso JSON y vuelve a pasar todos los argumentos manualmente en el caso
con progreso. Una opción nueva puede añadirse en un sitio y no en el otro.

**Recomendación**: un único `options`, con `callback` y
`normalize_permissions` condicionales, y una sola llamada.

### S3 — Cinco recorridos de árbol distintos

La lógica `os.walk` + symlinks + exclusión está repetida en:

- `core/compile.py` (`_iter_compile_sources`, líneas 35-55);
- `core/package.py` (`_iter_package_files`, líneas 134-146);
- `core/cleanup.py` (`_walk_project`, líneas 29-43);
- `validation/repository.py` (`_find_prohibited_binaries`, líneas 24-50);
- `discovery.py` (`get_source_files`, líneas 85-102).

Cada uno tiene exclusiones ligeramente distintas. Esto ya provocó el bug de
`.venv` en `clean`.

**Recomendación**: un `ProjectWalker` único con `PathPolicy(purpose=...)` para
package/compile/clean y un `Exclusions` con categorías (VCS, entornos, builds,
dev, herramientas).

### S4 — `console as click` en 17 módulos

`src/qgis_manager/cli/base.py` (línea 8), `cli/commands/deploy.py` (línea 18),
etc. Es un alias de compatibilidad que quedó tras eliminar `click`. Funciona,
pero engaña al lector, mantiene tests atados a `click` y dificulta una API de
consola más rica.

**Recomendación**: renombrar a `console` y actualizar los `patch(...click...)` a
`console`; sin cambio funcional.

### S5 — `CLIApp._build_parser` usa atributos privados de `argparse`

`src/qgis_manager/cli/app.py` (líneas 33-118) modifica
`parser._positionals.title`, `parser._optionals.title` y
`cmd_parser._positionals.title`. Es frágil entre versiones de Python y mezcla
presentación con parsing.

**Recomendación**: encapsular el layout en `HelpfulArgumentParser` o aceptar el
layout estándar; test de `--help` sin atributos privados.

## 4. Correctitud y seguridad secundaria

| Hallazgo | Evidencia | Recomendación |
| :--- | :--- | :--- |
| `install-deps` permite inyección de opciones de pip | `dependencies.py` (33-90): `cmd_base + ["--target", dest] + dependencies` | Validar PEP 508, insertar `--` y rechazar elementos que empiecen por `-` |
| `init --template` acepta rutas | `core/scaffold.py` (74-80): `templates / template` | Whitelist de templates y `resolve()` con comprobación de prefijo |
| ZIP sin límite de descompresión | `validation/artifact.py` (60-95) lee metadata/icon sin límite | Limitar `file_size` total/por archivo antes de `zf.read` |
| `set_project_version` no es atómico y solo admite comillas dobles | `toml_utils.py` (33-50) | Usar `write_text_atomic`; soportar `'...'` y `"..."` |
| `analyzer` sin timeout y con doble probe | `cli/analyzer.py` (8-39) | Cachear disponibilidad, añadir `timeout`, evitar `--version` por llamada |
| `package --json --repo-check` falla sin envelope | `cli/commands/package.py` (95-115) | Emitir siempre el envelope, también en fallo de compliance |
| `get_plugin_metadata` devuelve formas distintas | `metadata.py` (159-200): falta `version` en fallback malformado | Normalizar siempre `name`, `slug`, `version` |
| Errores globales silenciosos | `cli/base.py` (45-52), `cli/app.py` (120-154) | `--debug`/traceback y un `CliError` tipado; `logger.exception` |

## 5. Rendimiento y reproducibilidad

### P1 — El ZIP no garantiza orden reproducible

`discovery.py` (85-102) itera `project_root.iterdir()` sin ordenar;
`core/package.py` (147-165) escribe en ese orden. Los timestamps son
deterministas, pero el orden de miembros del ZIP puede variar entre sistemas de
archivos y cambiar el SHA256.

**Recomendación**: ordenar por `arcname` en `_collect_zip_items`; test con dos
órdenes de creación distintos.

### P2 — `clean` lanza un `git ls-files` por cada `.py` generado

`core/cleanup.py` (75-100) llama `_is_tracked` dentro del bucle de `.ui/.qrc`.
En un proyecto con muchos recursos son decenas/cientos de subprocesos.

**Recomendación**: obtener una sola vez el conjunto de archivos trackeados y
consultarlo en memoria.

### P3 — `count_compile_steps` y `compile_qt_resources` recorren el árbol dos veces

`core/compile.py` (218-238) cuenta `.qrc/.ui/.ts` y luego `compile_*` vuelve a
recorrer. En CLI con `--type all` se duplica el walk.

**Recomendación**: un `CompilePlan` que devuelva listas de archivos y total;
compilar ese plan.

### P4 — `plan_deploy` no usa el manifiesto

`plan_deploy` recalcula hashes con `_needs_copy` para cada archivo aunque exista
`DeployManifest`. El dry-run es más caro que el deploy real en proyectos
grandes.

**Recomendación**: `plan_deploy(..., manifest=...)` y reutilizar huellas; el
guard de C2 es requisito previo.

### P5 — `IgnoreMatcher` reevalúa todos los patrones por archivo

`ignore.py` (70-120) recorre patrones y reglas anidadas para cada path. En
packaging de muchos archivos puede ser el coste dominante.

**Recomendación**: precompilar patrones por directorio, cachear decisiones por
path y separar matching root/nested; medir antes de optimizar.

### P6 — `get_git_info` lanza dos procesos `git`

`core/package.py` (30-52) ejecuta `rev-parse` y `rev-list` por separado. Es
barato, pero puede combinarse o cachearse en CI con `--stamp`.

## 6. Duplicación de constantes de exclusión

Hay al menos cuatro fuentes de verdad:

- `DEFAULT_EXCLUDE_PATTERNS` y `DEV_DIRECTORIES` en `constants.py` (1-60);
- `_DEV_DIRS` en `validation/artifact.py` (11-25);
- `_COMPILE_EXCLUDED_DIRS` en `core/compile.py` (23-38);
- `_EXCLUDED_DIRS` en `core/cleanup.py` (12-27).

No son idénticas: `.agent`, `.ai-context`, `.mypy_cache` y `libs` aparecen en
unos sitios y no en otros. Es una fuente directa de inconsistencias entre
`package`, `deploy`, `clean`, `compile` y `validate`.

**Recomendación**: un módulo `paths/policy.py` con categorías y
`is_excluded(path, purpose)`. Los tests deben validar la política, no cada lista.

## 7. Prioridad

### `0.16.2` — seguridad/correctitud

1. `hooks list` sin ejecución + test de marcador.
2. Guard de destino en `plan_deploy` + test.
3. Swap atómico de `compile_docs` + test de fallo.
4. `dclean` con perfil absoluto + test.
5. Serialización de callbacks con `--jobs > 1`.
6. Orden determinista del ZIP + test de reproducibilidad.

### `0.17.0` — refactor estructural

1. `ProjectWalker`/`PathPolicy` único.
2. `DeployWorkflow` y `PackageWorkflow`.
3. Renombrar `console as click` → `console`.
4. Error boundary tipado + `--debug`.
5. `set_project_version` atómico y TOML con comillas simples.
6. Validación de `install-deps` y `--template`.

### `0.17.x` — rendimiento

1. Un solo inventario para compile/package/clean.
2. `CompilePlan` compartido.
3. `git ls-files` cacheado.
4. Matcher precompilado.
5. `plan_deploy` con manifiesto.

## 8. Tests que faltan

- `hooks list` no ejecuta código.
- `plan_deploy` con destino dentro del proyecto.
- `compile_docs` con fallo de `move`: la documentación anterior sigue existiendo.
- `dclean --profile /ruta/absoluta`.
- `compile --jobs 2` con callback registrando eventos.
- ZIP reproducible con orden de creación distinto.
- ZIP con metadata/icon desmesurados no consume memoria sin límite.
- `package --json` siempre emite envelope, también en fallo de compliance.

## 9. Conclusión

No hay spaghetti generalizado: los módulos están razonablemente separados y la
cobertura es alta. El riesgo se concentra en fronteras de confianza
(`hooks list`, templates, dependencias, ZIP), operaciones destructivas no
atómicas (`compile_docs`) y duplicación de políticas de recorrido. Antes de
optimizar rendimiento, cerrar los cinco puntos críticos; después, unificar
walkers/exclusiones, que es la optimización estructural con mayor retorno y
menor riesgo.
