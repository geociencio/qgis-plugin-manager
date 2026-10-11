"""Scaffolding of new QGIS plugin projects from bundled templates."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def init_plugin_project(
    path: Path,
    name: str,
    author: str,
    email: str,
    description: str = "A QGIS plugin.",
    template: str = "default",
) -> None:
    """Initialize a new QGIS plugin project from a bundled template."""
    from ..discovery import slugify
    from ..templating import render_template

    slug = slugify(name)
    class_name = name.replace(" ", "")
    project_dir = path / slug
    if project_dir.exists():
        raise FileExistsError(f"Directory {project_dir} already exists.")

    template_dir = Path(__file__).resolve().parent.parent / "templates" / template
    if not template_dir.is_dir():
        raise ValueError(f"Unknown template: {template}")

    project_dir.mkdir(parents=True)

    logger.info(
        f"🚀 Initializing new QGIS plugin: {name} in {project_dir} "
        f"(Template: {template})"
    )

    context = {
        "name": name,
        "slug": slug,
        "class_name": class_name,
        "description": description,
        "author": author,
        "email": email,
    }

    # Template filenames whose output name depends on the plugin slug.
    name_overrides = {
        "plugin.py": f"{slug}.py",
        "provider.py": f"{slug}_provider.py",
        "algorithm.py": f"{slug}_algorithm.py",
        "dockwidget.py": f"{slug}_dockwidget.py",
        "dockwidget_base.ui": f"{slug}_dockwidget_base.ui",
    }

    for tmpl in sorted(template_dir.glob("*.tmpl")):
        base_name = tmpl.name[: -len(".tmpl")]
        output_name = name_overrides.get(base_name, base_name)
        output_path = project_dir / output_name
        output_path.write_text(render_template(tmpl, **context), encoding="utf-8")
        logger.debug(f"  ✅ {output_name}")

    logger.info(f"✨ Project {name} initialized successfully.")
