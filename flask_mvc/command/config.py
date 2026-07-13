"""Configuration for Flask MVC CLI."""

import os
from pathlib import Path
from typing import Any, Dict, Optional


class CLIConfig:
    """Configuration settings for CLI commands."""

    # Default paths
    DEFAULT_CONTROLLERS_PATH = "app/controllers"
    DEFAULT_VIEWS_PATH = "app/views"
    DEFAULT_MODELS_PATH = "app/models"

    # Template configuration
    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

    # Controller template settings
    CONTROLLER_TEMPLATE = "base_controller.jinja2"

    # File encoding
    FILE_ENCODING = "utf-8"

    # CLI styling
    SUCCESS_COLOR = "green"
    ERROR_COLOR = "red"
    WARNING_COLOR = "yellow"
    INFO_COLOR = "blue"

    # Environment variables for overriding defaults
    ENV_PREFIX = "FLASK_MVC_"

    @classmethod
    def get_controllers_path(cls) -> str:
        """Get controllers path from environment or default.

        Returns:
            Controllers directory path
        """
        return os.getenv(
            f"{cls.ENV_PREFIX}CONTROLLERS_PATH", cls.DEFAULT_CONTROLLERS_PATH
        )

    @classmethod
    def get_templates_dir(cls) -> Path:
        """Get templates directory path.

        Returns:
            Templates directory path
        """
        custom_dir = os.getenv(f"{cls.ENV_PREFIX}TEMPLATES_DIR")
        if custom_dir:
            return Path(custom_dir)
        return cls.TEMPLATES_DIR

    @classmethod
    def get_file_encoding(cls) -> str:
        """Get file encoding from environment or default.

        Returns:
            File encoding string
        """
        return os.getenv(f"{cls.ENV_PREFIX}FILE_ENCODING", cls.FILE_ENCODING)
