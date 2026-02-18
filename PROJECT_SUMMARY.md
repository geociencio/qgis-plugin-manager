# PROJECT SUMMARY - qgis-plugin-manager
Analysis Date: 2026-02-18 15:24:22
Analyzer Version: 3.1.1 (Ai-Context-Core)

## 📊 KEY METRICS
- **Quality Score**: 79.4/100
- **Source Lines (SLOC)**: 3,050
- **Total Physical Lines**: 4,581
- **Maintainability**: 44.6
- **Test Coverage**: 13 test files

## 📁 STRUCTURE
**Total Modules**: 48

```tree
./
    .ai_context_cache.json
    .gitattributes
    .gitignore
    .pre-commit-config.yaml
    AI_CONTEXT.md
    CHANGELOG.md
    LICENSE
    ... (+10 more)
    src/
        qgis_manager/
            __init__.py
            cli.py
            config.py
            constants.py
            core.py
            dependencies.py
            discovery.py
            ... (+2 more)
            templates/
                default/
                    __init__.py.tmpl
                    metadata.txt.tmpl
                    plugin.py.tmpl
                processing/
                    provider.py.tmpl
                dockwidget/
            cli/
                __init__.py
                app.py
                base.py
                commands/
                    __init__.py
                    analyze.py
                    clean.py
                    compile.py
                    deploy.py
                    init.py
                    install_deps.py
                    ... (+1 more)
    tests/
        test_cli.py
        test_config.py
        test_core.py
        test_deployment_optimization.py
        test_discovery.py
        test_fix_exclusions.py
        test_hooks.py
        ... (+5 more)
    analysis_results/
        PROJECT_SUMMARY.md
        analyzer.log
        project_context.json
    docs/
        COMMIT_GUIDELINES.md
        CONTRIBUTING.md
        GITHUB_RELEASE_v0.3.1.md
        GITHUB_RELEASE_v0.3.2.md
        GITHUB_RELEASE_v0.3.3.md
        GITHUB_RELEASE_v0.4.0.md
        GITHUB_RELEASE_v0.4.1.md
        ... (+14 more)
    generator_export/
        GENERATOR_MANUAL.md
        generator.py
        templates/
            base/
                __init__.py.tmpl
                metadata.txt.tmpl
            processing/
                algorithm.py.tmpl
            gui/
                plugin.py.tmpl
            map_tool/
                plugin.py.tmpl
    dist/
        .gitignore
        qgis_manage-0.6.0-py3-none-any.whl
        qgis_manage-0.6.0.tar.gz
    antigravity-framerepo/
        BOOTSTRAP.md
        LICENSE
        README.md
        antigravity_framework_starter_kit.zip
        bootstrap.py
        pyproject.toml
        scaffold/
            AGENTS.md
            skills/
                agentic-memory.md
                coding-standards.md
                commit-standards.md
                data-science/
                    SKILL.md
            workflows/
                cierra-sesion.md
                ia-critic.md
                inicia-sesion.md
            ui/
                dialog_template.py
            processing/
                algorithm_template.py
            memory/
                AGENT_LESSONS.md
                agent_metrics.json
        scripts/
            skill_sync.py
        docs/
            AGENT_ARCHITECTURE.md
            UPGRADE_FRAMEWORK_GEN2.md
    scaffold/
        AGENTS.md
        skills/
            agentic-memory.md
            coding-standards.md
            commit-standards.md
            data-science/
                SKILL.md
                scripts/
                    generate_mock_data.py
                    validate_dataset.py
                examples/
                    eda_template.py
        workflows/
            cierra-sesion.md
            ia-critic.md
            inicia-sesion.md
        ui/
            dialog_template.py
        processing/
            algorithm_template.py
        memory/
            AGENT_LESSONS.md
            agent_metrics.json
```

## 🚨 CRITICAL ISSUES
### 🔒 Security Issues:
- **antigravity-framerepo/bootstrap.py**: 4 issues (Max: HIGH)
- **antigravity-framerepo/scaffold/skills/data-science/scripts/validate_dataset.py**: 1 issues (Max: HIGH)
- **antigravity-framerepo/scripts/skill_sync.py**: 2 issues (Max: HIGH)

## 💡 MAIN RECOMMENDATIONS
### src/qgis_manager/core.py
- Consider breaking down large logic
- Large module (600 lines)
### src/qgis_manager/ignore.py
- Consider breaking down large logic
### src/qgis_manager/validation.py
- Consider breaking down large logic

## 🏗️ DESIGN PATTERNS
### Decorator
- **get_ignore_func** in `src/qgis_manager/ignore.py` (50%)

## 🔄 GIT ANALYSIS

### 🔥 Hotspots
- `src/qgis_manager/core.py`: 16 commits
- `src/qgis_manager/cli.py`: 13 commits
- `tests/test_core.py`: 9 commits
- `src/qgis_manager/discovery.py`: 6 commits
- `tests/test_discovery.py`: 6 commits

## 📈 COMPLEXITY DISTRIBUTION
- **Average Complexity**: 8.06
- **Max Complexity**: 74
