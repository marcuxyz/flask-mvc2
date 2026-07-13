"""Generators for MVC components."""

from pathlib import Path
from typing import Optional

from .config import CLIConfig
from .exceptions import ControllerGenerationError, InvalidControllerNameError
from .file_handler import FileHandler
from .name_utils import NameUtils
from .template_renderer import TemplateRenderer


class ControllerGenerator:
    """Generates controller files using templates."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the controller generator.

        Args:
            templates_dir: Path to templates directory. If None, uses default location.
        """
        templates_dir = templates_dir or CLIConfig.get_templates_dir()

        self.template_renderer = TemplateRenderer(templates_dir)
        self.file_handler = FileHandler()
        self.name_utils = NameUtils()
        self.config = CLIConfig()

    def generate(
        self, name: str, output_path: Optional[str] = None, force: bool = False
    ) -> Path:
        """Generate a new controller file.

        Args:
            name: Name of the controller
            output_path: Directory where to create the controller
            force: Whether to overwrite existing files

        Returns:
            Path to the created controller file

        Raises:
            ControllerGenerationError: If generation fails
            InvalidControllerNameError: If controller name is invalid
        """
        try:
            # Validate controller name
            self.name_utils.validate_controller_name(name)

            # Use default path if none provided
            output_path = output_path or CLIConfig.get_controllers_path()

            # Normalize names
            controller_name = self.name_utils.normalize_controller_name(name)
            class_name = self.name_utils.generate_class_name(controller_name)

            # Prepare paths
            output_dir = Path(output_path)
            controller_file = output_dir / f"{controller_name}.py"

            # Check if file already exists (unless force is True)
            if not force and self.file_handler.file_exists(controller_file):
                raise ControllerGenerationError(
                    f"Controller '{controller_name}' already exists at {controller_file}. "
                    f"Use --force to overwrite."
                )

            # Ensure output directory exists
            self.file_handler.ensure_directory_exists(output_dir)

            # Render template
            content = self.template_renderer.render(
                self.config.CONTROLLER_TEMPLATE, {"class_name": class_name}
            )

            # Write file
            self.file_handler.write_file(controller_file, content)

            return controller_file

        except Exception as e:
            if isinstance(e, (ControllerGenerationError, InvalidControllerNameError)):
                raise
            raise ControllerGenerationError(f"Failed to generate controller: {e}") from e
