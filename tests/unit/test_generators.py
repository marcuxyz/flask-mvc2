"""Tests for generators module."""

import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil

from flask_mvc.commands.controller.generator import Generator as ControllerGenerator
from flask_mvc.commands.exceptions import (
    ControllerGenerationError,
    InvalidControllerNameError,
)


class TestControllerGenerator:
    """Test cases for ControllerGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.templates_dir = self.temp_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Create a mock template file
        template_file = self.templates_dir / "base_controller.jinja2"
        template_content = """class {{ class_name }}:
    \"\"\"Controller class.\"\"\"

    def index(self):
        return "Hello from {{ class_name }}"
"""
        template_file.write_text(template_content)

        self.generator = ControllerGenerator(templates_dir=self.templates_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_init_with_templates_dir(self):
        """Test ControllerGenerator initialization with custom templates directory."""
        generator = ControllerGenerator(templates_dir=self.templates_dir)

        assert generator.template_renderer is not None
        assert generator.file_handler is not None
        assert generator.name_utils is not None
        assert generator.config is not None

    @patch("flask_mvc.commands.controller.generator.CLIConfig.get_templates_dir")
    def test_init_without_templates_dir(self, mock_get_templates_dir):
        """Test ControllerGenerator initialization with default templates directory."""
        mock_get_templates_dir.return_value = self.templates_dir

        generator = ControllerGenerator()

        assert generator.template_renderer is not None
        assert generator.file_handler is not None
        assert generator.name_utils is not None
        assert generator.config is not None
        mock_get_templates_dir.assert_called_once()

    def test_generate_controller_success(self):
        """Test successful controller generation."""
        output_dir = self.temp_dir / "controllers"

        with (
            patch.object(
                self.generator.name_utils, "validate_controller_name"
            ) as mock_validate,
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(
                self.generator.name_utils, "generate_class_name"
            ) as mock_class_name,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
            patch.object(
                self.generator.file_handler, "ensure_directory_exists"
            ) as mock_ensure_dir,
            patch.object(self.generator.file_handler, "write_file") as mock_write,
            patch.object(self.generator.template_renderer, "render") as mock_render,
        ):
            mock_normalize.return_value = "test_controller"
            mock_class_name.return_value = "TestController"
            mock_exists.return_value = False
            mock_render.return_value = "class TestController:\n    pass"

            result = self.generator.generate("test", str(output_dir))

            expected_path = output_dir / "test_controller.py"
            assert result == expected_path

            mock_validate.assert_called_once_with("test")
            mock_normalize.assert_called_once_with("test")
            mock_class_name.assert_called_once_with("test_controller")
            mock_exists.assert_called_once_with(expected_path)
            mock_ensure_dir.assert_called_once_with(output_dir)
            mock_render.assert_called_once_with(
                self.generator.config.CONTROLLER_TEMPLATE,
                {"class_name": "TestController"},
            )
            mock_write.assert_called_once_with(
                expected_path, "class TestController:\n    pass"
            )

    @patch("flask_mvc.commands.controller.generator.CLIConfig.get_controllers_path")
    def test_generate_controller_default_path(self, mock_get_path):
        """Test controller generation with default output path."""
        mock_get_path.return_value = "app/controllers"
        output_dir = Path("app/controllers")

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(
                self.generator.name_utils, "generate_class_name"
            ) as mock_class_name,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
            patch.object(self.generator.file_handler, "ensure_directory_exists"),
            patch.object(self.generator.file_handler, "write_file"),
            patch.object(self.generator.template_renderer, "render") as mock_render,
        ):
            mock_normalize.return_value = "home_controller"
            mock_class_name.return_value = "HomeController"
            mock_exists.return_value = False
            mock_render.return_value = "class HomeController:\n    pass"

            result = self.generator.generate("home")

            expected_path = output_dir / "home_controller.py"
            assert result == expected_path
            mock_get_path.assert_called_once()

    def test_generate_controller_file_exists_no_force(self):
        """Test controller generation when file exists and force is False."""
        output_dir = self.temp_dir / "controllers"

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
        ):
            mock_normalize.return_value = "existing_controller"
            mock_exists.return_value = True

            with pytest.raises(ControllerGenerationError) as exc_info:
                self.generator.generate("existing", str(output_dir), force=False)

            assert "already exists" in str(exc_info.value)
            assert "Use --force to overwrite" in str(exc_info.value)

    def test_generate_controller_file_exists_with_force(self):
        """Test controller generation when file exists and force is True."""
        output_dir = self.temp_dir / "controllers"

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(
                self.generator.name_utils, "generate_class_name"
            ) as mock_class_name,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
            patch.object(self.generator.file_handler, "ensure_directory_exists"),
            patch.object(self.generator.file_handler, "write_file") as mock_write,
            patch.object(self.generator.template_renderer, "render") as mock_render,
        ):
            mock_normalize.return_value = "existing_controller"
            mock_class_name.return_value = "ExistingController"
            mock_exists.return_value = True
            mock_render.return_value = "class ExistingController:\n    pass"

            result = self.generator.generate("existing", str(output_dir), force=True)

            expected_path = output_dir / "existing_controller.py"
            assert result == expected_path
            mock_write.assert_called_once()

    def test_generate_controller_invalid_name_error(self):
        """Test controller generation with invalid name."""
        with patch.object(
            self.generator.name_utils, "validate_controller_name"
        ) as mock_validate:
            mock_validate.side_effect = InvalidControllerNameError("Invalid name")

            with pytest.raises(InvalidControllerNameError):
                self.generator.generate("123invalid")

    def test_generate_controller_template_render_error(self):
        """Test controller generation when template rendering fails."""
        output_dir = self.temp_dir / "controllers"

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(
                self.generator.name_utils, "generate_class_name"
            ) as mock_class_name,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
            patch.object(self.generator.file_handler, "ensure_directory_exists"),
            patch.object(self.generator.template_renderer, "render") as mock_render,
        ):
            mock_normalize.return_value = "test_controller"
            mock_class_name.return_value = "TestController"
            mock_exists.return_value = False
            mock_render.side_effect = Exception("Template error")

            with pytest.raises(ControllerGenerationError) as exc_info:
                self.generator.generate("test", str(output_dir))

            assert "Failed to generate controller" in str(exc_info.value)

    def test_generate_controller_file_write_error(self):
        """Test controller generation when file writing fails."""
        output_dir = self.temp_dir / "controllers"

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(
                self.generator.name_utils, "generate_class_name"
            ) as mock_class_name,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
            patch.object(self.generator.file_handler, "ensure_directory_exists"),
            patch.object(self.generator.file_handler, "write_file") as mock_write,
            patch.object(self.generator.template_renderer, "render") as mock_render,
        ):
            mock_normalize.return_value = "test_controller"
            mock_class_name.return_value = "TestController"
            mock_exists.return_value = False
            mock_render.return_value = "class TestController:\n    pass"
            mock_write.side_effect = Exception("Write error")

            with pytest.raises(ControllerGenerationError) as exc_info:
                self.generator.generate("test", str(output_dir))

            assert "Failed to generate controller" in str(exc_info.value)

    def test_generate_controller_directory_creation_error(self):
        """Test controller generation when directory creation fails."""
        output_dir = self.temp_dir / "controllers"

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(
                self.generator.name_utils, "generate_class_name"
            ) as mock_class_name,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
            patch.object(
                self.generator.file_handler, "ensure_directory_exists"
            ) as mock_ensure_dir,
            patch.object(self.generator.template_renderer, "render") as mock_render,
        ):
            mock_normalize.return_value = "test_controller"
            mock_class_name.return_value = "TestController"
            mock_exists.return_value = False
            mock_render.return_value = "class TestController:\n    pass"
            mock_ensure_dir.side_effect = Exception("Directory error")

            with pytest.raises(ControllerGenerationError) as exc_info:
                self.generator.generate("test", str(output_dir))

            assert "Failed to generate controller" in str(exc_info.value)

    def test_generate_controller_complex_name(self):
        """Test controller generation with complex names."""
        output_dir = self.temp_dir / "controllers"

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(
                self.generator.name_utils, "generate_class_name"
            ) as mock_class_name,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
            patch.object(self.generator.file_handler, "ensure_directory_exists"),
            patch.object(self.generator.file_handler, "write_file") as mock_write,
            patch.object(self.generator.template_renderer, "render") as mock_render,
        ):
            mock_normalize.return_value = "api_v1_user_controller"
            mock_class_name.return_value = "ApiV1UserController"
            mock_exists.return_value = False
            mock_render.return_value = "class ApiV1UserController:\n    pass"

            result = self.generator.generate("api_v1_user", str(output_dir))

            expected_path = output_dir / "api_v1_user_controller.py"
            assert result == expected_path

    def test_generate_controller_re_raise_known_exceptions(self):
        """Test that known exceptions are re-raised without wrapping."""
        with patch.object(
            self.generator.name_utils, "validate_controller_name"
        ) as mock_validate:
            # Test InvalidControllerNameError is re-raised
            mock_validate.side_effect = InvalidControllerNameError("Invalid name")

            with pytest.raises(InvalidControllerNameError):
                self.generator.generate("invalid")

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(self.generator.name_utils, "normalize_controller_name"),
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
        ):
            # Test ControllerGenerationError is re-raised
            mock_exists.side_effect = ControllerGenerationError("Generation error")

            with pytest.raises(ControllerGenerationError):
                self.generator.generate("test")

    def test_generate_controller_integration_with_real_template(self):
        """Test controller generation with actual template rendering."""
        output_dir = self.temp_dir / "controllers"
        output_dir.mkdir(parents=True, exist_ok=True)

        with (
            patch.object(self.generator.name_utils, "validate_controller_name"),
            patch.object(
                self.generator.name_utils, "normalize_controller_name"
            ) as mock_normalize,
            patch.object(
                self.generator.name_utils, "generate_class_name"
            ) as mock_class_name,
            patch.object(self.generator.file_handler, "file_exists") as mock_exists,
        ):
            mock_normalize.return_value = "test_controller"
            mock_class_name.return_value = "TestController"
            mock_exists.return_value = False

            result = self.generator.generate("test", str(output_dir))

            # Check that file was actually created
            assert result.exists()
            content = result.read_text()
            assert "TestController" in content
            assert "class TestController:" in content
