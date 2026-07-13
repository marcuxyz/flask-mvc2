"""Template rendering utilities for Flask MVC CLI."""

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from .exceptions import TemplateNotFoundError


class TemplateRenderer:
    """Handles template rendering for code generation."""

    def __init__(self, templates_dir: Path):
        """Initialize the template renderer.

        Args:
            templates_dir: Path to the templates directory
        """
        self.templates_dir = templates_dir
        self._env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of the template file
            context: Variables to pass to the template

        Returns:
            Rendered template content

        Raises:
            TemplateNotFoundError: If template file is not found
        """
        try:
            template = self._env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise TemplateNotFoundError(
                f"Template '{template_name}' not found in {self.templates_dir}"
            ) from e
