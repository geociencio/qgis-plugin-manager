# PROJECT SUMMARY - qgis-plugin-manager
Analysis Date: 2026-04-05 17:09:33
Analyzer Version: 3.1.1 (Ai-Context-Core)

## 📊 KEY METRICS
- **Quality Score**: 74.5/100
- **Source Lines (SLOC)**: 3,425
- **Total Physical Lines**: 5,113
- **Maintainability**: 41.3
- **Test Coverage**: 14 test files

## 📁 STRUCTURE
**Total Modules**: 42

```tree
./
    .ai_context_cache.json
    .gitattributes
    .gitignore
    .pre-commit-config.yaml
    AI_CONTEXT.md
    CHANGELOG.md
    LICENSE
    ... (+11 more)
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
                    bump.py
                    clean.py
                    compile.py
                    deploy.py
                    hooks.py
                    ... (+3 more)
    tests/
        test_cli.py
        test_config.py
        test_core.py
        test_deployment_optimization.py
        test_discovery.py
        test_fix_exclusions.py
        test_hooks.py
        ... (+6 more)
    analysis_results/
        PROJECT_SUMMARY.md
        analyzer.log
        project_context.json
    docs/
        CHANGELOG.md
        DEVELOPMENT_LOG.md
        research/
            CLI_EXPANSION_PROPOSAL.md
            COMPETITIVE_ANALYSIS.md
            RECOMMENDATIONS.md
            distribution_research.md
            qgis_manager_dev_roadmap.md
        plans/
            badges_expansion_plan.md
            bump_implementation_plan.md
            cli_refactor_plan.md
            deployment_optimization_plan.md
            distribution_plan.md
            documentation_reorg_plan.md
            hooks_expansion_plan.md
            ... (+4 more)
        walkthroughs/
            walkthrough.md
        releases/
            GITHUB_RELEASE_v0.3.1.md
            GITHUB_RELEASE_v0.3.2.md
            GITHUB_RELEASE_v0.3.3.md
            GITHUB_RELEASE_v0.4.0.md
            GITHUB_RELEASE_v0.4.1.md
            GITHUB_RELEASE_v0.5.0.md
            GITHUB_RELEASE_v0.6.0.md
            ... (+12 more)
        guides/
            TUTORIAL.md
            uv_modernization_guide.md
        standards/
            COMMIT_GUIDELINES.md
            CONTRIBUTING.md
        maintenance/
            SESSION_LOG_modernization.md
            infrastructure_upgrade_20260218.md
            sesion_2026-02-18_v0.6.1_release.md
            sesion_2026-02-18_v0.6.1_release_task.md
            session_2026-04-05_gen5_sync.md
            v0.6.1_bug_patch_report.md
        examples/
        architecture/
            CORE_VALIDATION_IMPROVEMENTS.md
            IGNORE_PARSER_IMPROVEMENTS.md
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
        qgis_manage-0.6.4-py3-none-any.whl
        qgis_manage-0.6.4.tar.gz
    scaffold/
        mining/
            skills/
                geological-logic/
                    SKILL.md
        qgis/
            skills/
                qa-docker/
                    SKILL.md
                qgis-core/
                    SKILL.md
                qgis-migration-4x/
                    SKILL.md
                ui-framework/
                    SKILL.md
            workflows/
                audit-plugin.md
                release-plugin.md
                run-tests-in-qgis.md
    scripts/
        mcp_server.py
        security_scan.py
        skill_sync.py
```

## 🚨 CRITICAL ISSUES
### 🔒 Security Issues:
- **bootstrap.py**: 4 issues (Max: HIGH)
- **scripts/mcp_server.py**: 4 issues (Max: HIGH)
- **scripts/security_scan.py**: 1 issues (Max: HIGH)

## 💡 MAIN RECOMMENDATIONS
### scripts/mcp_server.py
- Consider breaking down large logic
### scripts/security_scan.py
- Consider breaking down large logic
### src/qgis_manager/cli/commands/bump.py
- Consider breaking down large logic

## 🏗️ DESIGN PATTERNS
### Decorator
- **get_ignore_func** in `src/qgis_manager/ignore.py` (50%)

## 🔄 GIT ANALYSIS
### Code Churn (last 30 days)
- **Files Changed**: 67
- **Additions**: +2001
- **Deletions**: -2202
- **Total Churn**: 4203

### 🔥 Hotspots
- `src/qgis_manager/core.py`: 20 commits
- `src/qgis_manager/cli.py`: 14 commits
- `src/qgis_manager/discovery.py`: 12 commits
- `tests/test_core.py`: 12 commits
- `src/qgis_manager/validation.py`: 8 commits

## 📈 COMPLEXITY DISTRIBUTION
- **Average Complexity**: 11.40
- **Max Complexity**: 85
