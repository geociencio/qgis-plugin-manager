"""Scaffolding of new QGIS plugin projects from bundled templates."""

import keyword
import logging
import re
import unicodedata
from pathlib import Path

logger = logging.getLogger(__name__)


def _class_name_from(name: str) -> str:
    """Return a valid ASCII PascalCase Python identifier for a plugin name.

    Hyphens, parentheses, accents and other separators are removed instead of
    being copied into the generated class name (which used to produce invalid
    Python such as ``class My-WeirdPlugin``).

    Args:
        name: Human-readable plugin name.

    Returns:
        A valid Python identifier derived from ``name``.
    """
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[A-Za-z0-9]+", ascii_name)
    identifier = "".join(word[:1].upper() + word[1:] for word in words) or "Plugin"
    if identifier[0].isdigit():
        identifier = f"_{identifier}"
    if keyword.iskeyword(identifier):
        identifier = f"{identifier}Plugin"
    return identifier


def init_plugin_project(
    path: Path,
    name: str,
    author: str,
    email: str,
    description: str = "A QGIS plugin.",
    template: str = "default",
) -> None:
    """Initialize a new QGIS plugin project from a bundled template.

    Args:
        path: Directory where the project folder will be created.
        name: Human-readable plugin name.
        author: Plugin author.
        email: Author email.
        description: Plugin description.
        template: Bundled template name (``default``, ``processing`` or
            ``dockwidget``).

    Raises:
        ValueError: If the name cannot produce a safe slug or the template is
            unknown.
        FileExistsError: If the target project directory already exists.
    """
    from ..naming import slugify, validate_slug
    from ..templating import render_template

    slug = slugify(name)
    validate_slug(slug, source="plugin name")
    class_name = _class_name_from(name)
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
