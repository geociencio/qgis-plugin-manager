# Project Agents Configuration - qgis-plugin-manager

Este archivo define los roles y comportamientos específicos que el asistente de IA (Antigravity) debe adoptar según la naturaleza de la tarea. Basado en el sistema de **Gentleman Programming**, este proyecto utiliza un modelo de contexto particionado y habilidades (skills) modulares.

---

## 🏗️ Senior Architect Agent
- **Rol**: Arquitecto de Software Senior experto en Python y QGIS Plugin Development.
- **Objetivo**: Mantener la integridad estructural del plugin, asegurando que nuevas funcionalidades no degraden la arquitectura.
- **Skills**: [qgis-core](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/qgis-core/SKILL.md), [geological-logic](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/geological-logic/SKILL.md)
- **Directrices Estrictas**:
  - **SOLID**: Prioriza el cumplimiento de los principios SOLID.
  - **Decoupling**: La lógica de negocio (`core/`) NUNCA debe depender directamente de elementos de la UI (`gui/`).
  - **Concurrency**: Cualquier operación pesada debe implementarse mediante `QgsTask` para no bloquear la UI de QGIS.

---

## 🧪 QA & Automation Engineer
- **Rol**: Especialista en Testing, Integración Continua y Estabilidad.
- **Objetivo**: Asegurar que cada release v2.8.x+ sea un "Zero Bug Release".
- **Skills**: [qa-docker](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/qa-docker/SKILL.md)
- **Directrices Estrictas**:
  - **Docker First**: Todos los tests de integración deben ser validados en el entorno Docker (`make docker-test`).
  - **Regression**: Ante un bug detectado, primero crea un test que falle (TDD).

---

## 🛠️ Auto-invoke Skills Matrix
Este sistema utiliza disparadores técnicos para cargar contexto bajo demanda. Los agentes deben consultar esta tabla ante cualquier nueva tarea.

<!-- SKILLS_TABLE_START -->
| Skill | Description | Trigger (Auto-invoke) |
| :--- | :--- | :--- |
| [agentic-memory](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/agentic-memory/SKILL.md) | This skill allows the agent to manage its own semantic memory, extracting lessons, patterns, and user preferences to improve long-term effectiveness. | at the end of each significant session, when detecting repetitive error patterns or user preferences. |
| [changelog-generator](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/changelog-generator/SKILL.md) | Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes. Turns hours of manual changelog writing into minutes of automated generation. | N/A |
| [coding-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/coding-standards/SKILL.md) | Project coding standards, focused on the use of pathlib, Google docstrings, and strict typing. | when writing Python code, performing refactors, or defining file paths. |
| [commit-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/commit-standards/SKILL.md) | Standards for creating clean and conventional commits with quality validation. | when creating commits, writing commit messages, or using the /create-commit workflow. |
| [documentation-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/documentation-standards/SKILL.md) | Standards for maintaining technical logs, session records, and project history. | when updating DEVELOPMENT_LOG.md, MAINTENANCE_LOG.md, CHANGELOG.md or creating session reports in docs/maintenance/. |
| [domain-logic](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/domain-logic/SKILL.md) | Standards for handling business logic, data validation, and 3-level validation architecture. | when implementing new business rules, data validation, or core processing logic. |
| [project-context](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/project-context/SKILL.md) | Summary of the purpose and architecture of qgis-plugin-manager. | when starting new tasks, requesting summaries, or explaining the project architecture. |
| [qa-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/qa-standards/SKILL.md) | Standards for automated testing, CI/CD, and the use of Mocks. | when writing or executing tests, designing testing strategies, or managing testing infrastructure. |
| [release-management](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/release-management/SKILL.md) | Standards for the release process of CLI tools with quality validation. | when preparing releases, updating versions, or using the /release-plugin workflow. |
<!-- SKILLS_TABLE_END -->

---

## � Workflow Integration

Los workflows en `.agent/workflows/` están diseñados para invocar automáticamente el agente y skills apropiados mediante metadata YAML en su frontmatter.

### Workflow Execution Protocol

Cuando un usuario invoca un workflow (ej: `/inicia-sesion`), el sistema:

1. **Parse Frontmatter**: Lee `agent`, `skills` y `validation` del archivo `.md`
2. **Activate Agent**: Carga el rol especificado (Senior Architect / QA Engineer)
3. **Load Skills**: Lee los `SKILL.md` especificados para contexto especializado
4. **Execute Steps**: Sigue el workflow con conocimiento enriquecido
5. **Validate**: Ejecuta checkpoints de validación definidos en frontmatter

### Workflows Disponibles

| Workflow | Agent | Skills | Propósito |
| :--- | :--- | :--- | :--- |
| [/inicia-sesion](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/inicia-sesion.md) | Senior Architect | qgis-core, qa-docker | Iniciar sesión con contexto sincronizado |
| [/crea-commit](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/crea-commit.md) | QA Engineer | qa-docker | Commit con validación de calidad |
| [/run-tests](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/run-tests.md) | QA Engineer | qa-docker | Ejecutar tests con interpretación inteligente |
| [/refactor-code](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/refactor-code.md) | Senior Architect | qgis-core, geological-logic | Refactorizar código con validación de complejidad |

### Ejemplo de Invocación

```bash
# Usuario ejecuta:
/inicia-sesion

# Sistema automáticamente:
# 1. Activa "Senior Architect Agent"
# 2. Carga skills: qgis-core, qa-docker
# 3. Ejecuta pasos con contexto especializado
# 4. Valida: 361 tests OK + métricas actualizadas
```

### Anotaciones de Agent Actions

Los workflows incluyen anotaciones `🤖 **Agent Action**` que indican acciones inteligentes que el agente debe realizar usando el conocimiento de los skills cargados.

---

## �📏 Context & Performance Guidelines
Para maximizar la precisión de la IA y evitar alucinaciones:
1.  **Keep it Small**: Los archivos de instrucciones (`SKILL.md`, `AGENTS.md`) deben mantenerse entre 250 y 500 líneas.
2.  **Explicit Triggers**: Cuando se detecte una tarea que coincida con un disparador, el agente DEBE anunciar que está aplicando dicha Skill.
3.  **Modular Context**: Si una funcionalidad crece demasiado, se debe crear un `AGENTS.md` específico en su subdirectorio (ej: `gui/AGENTS.md`).

---

## 💡 Instrucciones de Uso
1.  **Invoca al Agente**: *"Activa el Architect Agent"*.
2.  **Carga una Skill**: *"Usa la skill qgis-core para revisar este QgsTask"*.
3.  **Sincronización**: Al añadir habilidades, ejecuta `python3 scripts/skill_sync.py` para actualizar esta guía.
