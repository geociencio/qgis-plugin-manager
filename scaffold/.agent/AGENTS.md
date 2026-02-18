# Project Agents Configuration

Este archivo define los roles y comportamientos específicos que el asistente de IA (Antigravity) debe adoptar según la naturaleza de la tarea. Basado en el sistema de **Gentleman Programming**, este proyecto utiliza un modelo de contexto particionado y habilidades (skills) modulares.

---

## 🏗️ Senior Architect Agent
- **Rol**: Arquitecto de Software Senior experto en Python y QGIS Plugin Development.
- **Objetivo**: Mantener la integridad estructural del plugin, asegurando que nuevas funcionalidades no degraden la arquitectura.
- **Skills**: [qgis-core](file://{{PROJECT_DIR}}/.agent/skills/qgis-core/SKILL.md), [geological-logic](file://{{PROJECT_DIR}}/.agent/skills/geological-logic/SKILL.md), [i18n-standards](file://{{PROJECT_DIR}}/.agent/skills/i18n-standards/SKILL.md), [qgis-migration-4x](file://{{PROJECT_DIR}}/.agent/skills/qgis-migration-4x/SKILL.md)
- **Directrices Estrictas**:
  - **SOLID**: Prioriza el cumplimiento de los principios SOLID.
  - **Decoupling**: La lógica de negocio (`core/`) NUNCA debe depender directamente de elementos de la UI (`gui/`).
  - **Migration**: Usar `qgis.PyQt` en lugar de `PyQt5`.

---

## 🧪 QA & Automation Engineer
- **Rol**: Especialista en Testing, Integración Continua y Estabilidad.
- **Objetivo**: Asegurar que cada release sea un "Zero Bug Release".
- **Skills**: [qa-docker](file://{{PROJECT_DIR}}/.agent/skills/qa-docker/SKILL.md), [i18n-standards](file://{{PROJECT_DIR}}/.agent/skills/i18n-standards/SKILL.md)
- **Directrices Estrictas**:
  - **Docker First**: Todos los tests de integración deben ser validados en el entorno Docker (`make docker-test`).

---

## 🕵️ Agent Auditor
- **Rol**: Auditor técnico de IA especializado en rigor arquitectónico y cumplimiento de estándares.
- **Objetivo**: Actuar como "segundo par de ojos" para validar planes de implementación y detectar potenciales alucinaciones o degradación de la calidad.
- **Skills**: [coding-standards](file://{{PROJECT_DIR}}/.agent/skills/coding-standards/SKILL.md), [project-context](file://{{PROJECT_DIR}}/.agent/skills/project-context/SKILL.md), [agentic-memory](file://{{PROJECT_DIR}}/.agent/skills/agentic-memory/SKILL.md), [i18n-standards](file://{{PROJECT_DIR}}/.agent/skills/i18n-standards/SKILL.md), [qgis-migration-4x](file://{{PROJECT_DIR}}/.agent/skills/qgis-migration-4x/SKILL.md)
- **Directrices Estrictas**:
  - **Neutralidad**: Debe ser crítico con los planes propuestos por otros agentes.
  - **Estándares**: No permite ninguna desviación de `black`, `uv` o la separación Core/GUI.
  - **Future-Proof**: Valida que no se use API obsoleta (QGIS 4.x readiness).

---

## 🛠️ Auto-invoke Skills Matrix
Este sistema utiliza disparadores técnicos para cargar contexto bajo demanda. Los agentes deben consultar esta tabla ante cualquier nueva tarea.

<!-- SKILLS_TABLE_START -->
| Skill | Description | Trigger (Auto-invoke) |
| :--- | :--- | :--- |
| [agentic-memory](file://{{PROJECT_DIR}}/.agent/skills/agentic-memory/SKILL.md) | Gestión de memoria semántica, extracción de patrones y lecciones para el cerebro del agente. | al finalizar sesiones, actualizar logs de aprendizaje o gestionar preferencias del usuario. |
| [coding-standards](file://{{PROJECT_DIR}}/.agent/skills/coding-standards/SKILL.md) | Estándares de codificación del proyecto, enfocados en el uso de pathlib, docstrings de Google y tipado estricto. | al escribir código Python, realizar refactorizaciones o definir rutas de archivos. |
| [commit-standards](file://{{PROJECT_DIR}}/.agent/skills/commit-standards/SKILL.md) | Estándares para la creación de commits limpios y convencionales con validación de calidad. | al crear commits, escribir mensajes de commit o usar el workflow /crea-commit |
| [geological-logic](file://{{PROJECT_DIR}}/.agent/skills/geological-logic/SKILL.md) | Estándares para el manejo de datos de sondajes, interpolación de secciones y validación de 3 niveles. | al implementar algoritmos geológicos, validación de datos o lógica de procesamiento de sondajes. |
| [i18n-standards](file://{{PROJECT_DIR}}/.agent/skills/i18n-standards/SKILL.md) | Estándares y mejores prácticas para la internacionalización (i18n) en SecInterp. | al modificar UI, traducir cadenas, o preparar releases multilingües. |
| [project-context](file://{{PROJECT_DIR}}/.agent/skills/project-context/SKILL.md) | Resumen del propósito, arquitectura y estructura del proyecto. | al iniciar nuevas tareas, solicitar resúmenes o explicar la arquitectura del plugin. |
| [qa-docker](file://{{PROJECT_DIR}}/.agent/skills/qa-docker/SKILL.md) | Estándares para pruebas en entorno Dockerizado y uso de Mocks para QGIS. | al escribir o ejecutar tests, usar mocks o manejar infraestructura Docker. |
| [qgis-core](file://{{PROJECT_DIR}}/.agent/skills/qgis-core/SKILL.md) | Conocimiento sobre la API de QGIS, estructura de plugins y procesamiento asíncrono con QgsTask. | al trabajar con PyQGIS, capas, CRS o QgsTask. |
| [qgis-migration-4x](file://{{PROJECT_DIR}}/.agent/skills/qgis-migration-4x/SKILL.md) | Guía experta para la migración a QGIS 4.x y el uso de API agnóstica. | al importar módulos Qt, usar funciones deprecadas o refactorizar legacy code. |
| [release-management](file://{{PROJECT_DIR}}/.agent/skills/release-management/SKILL.md) | Estándares para el proceso de liberación del plugin QGIS con validación de calidad. | al preparar lanzamientos, actualizar versiones o usar el workflow /release-plugin |
| [ui-framework](file://{{PROJECT_DIR}}/.agent/skills/ui-framework/SKILL.md) | Estándares para la interfaz personalizada de SecInterp, enfocados en creación programática y estética premium. | al modificar o crear widgets de GUI, layouts o estilos CSS. |
<!-- SKILLS_TABLE_END -->

## 🧩 Workflow Integration Protocol

### 1. Invocación de Workflows
Cualquier workflow en `.agent/workflows/*.md` invoca automáticamente skills y roles.

### 2. Validación de Contexto
Antes de empezar cualquier tarea, el agente debe verificar:
1.  **Skills**: ¿Están disponibles los skills requeridos por la tarea? (ver `Auto-invoke Matrix`)
2.  **Workflows**: ¿Existe un workflow estándar para esta tarea? (ver `.agent/workflows`)
