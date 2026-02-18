# Implementation Plan: Documentation Reorganization

Reorganize the `docs/` directory into a professional hierarchical structure based on `.agent` standards and project lifecycle needs.

## Proposed Structure

```
docs/
├── guides/            # Tutorials, how-to, setup guides
├── maintenance/       # Session logs, maintenance tasks
├── plans/             # Technical implementation plans
├── releases/          # Release notes and version highlights
├── research/          # Technical research and competitive analysis
├── standards/         # Coding, commit, and quality standards
└── walkthroughs/      # Proof of work and feature demonstrations
```

## Proposed Changes

### [Migration]

#### [MOVE] `docs/RELEASE_NOTES_v*.md` -> `docs/releases/`
#### [MOVE] `docs/GITHUB_RELEASE_v*.md` -> `docs/releases/`
#### [MOVE] `docs/COMMIT_GUIDELINES.md` -> `docs/standards/`
#### [MOVE] `docs/TUTORIAL.md` -> `docs/guides/`
#### [MOVE] `docs/uv_modernization_guide.md` -> `docs/guides/`
#### [MOVE] `docs/RECOMMENDATIONS.md` -> `docs/research/`
#### [MOVE] `docs/qgis_manager_dev_roadmap.md` -> `docs/research/`

### [Integration from current session]
Move relevant artifacts from `brain/` to the new `docs/` structure:
- `COMPETITIVE_ANALYSIS.md` -> `docs/research/`
- `distribution_research.md` -> `docs/research/`
- All `*_plan.md` -> `docs/plans/`
- `walkthrough.md` -> `docs/walkthroughs/`

## Verification Plan
### Manual Verification
- Verify that no links in `README.md` are broken.
- Ensure all directories are correctly populated.
