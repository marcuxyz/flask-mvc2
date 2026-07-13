"""Name utilities for Flask MVC CLI."""

import re

from .exceptions import InvalidControllerNameError


class NameUtils:
    """Utility class for handling naming conventions."""

    @staticmethod
    def validate_controller_name(name: str) -> None:
        """Validate controller name format.

        Args:
            name: The controller name to validate

        Raises:
            InvalidControllerNameError: If name is invalid
        """
        if not name:
            raise InvalidControllerNameError("Controller name cannot be empty")

        if not re.match(r"^[a-zA-Z]\w*$", name):
            raise InvalidControllerNameError(
                "Controller name must start with a letter and contain only "
                "letters, numbers, and underscores"
            )

    @staticmethod
    def normalize_controller_name(name: str) -> str:
        """Normalize controller name by adding _controller suffix if needed.

        Args:
            name: The controller name to normalize

        Returns:
            Normalized controller name with _controller suffix
        """
        NameUtils.validate_controller_name(name)

        if not name.endswith("_controller"):
            return f"{name}_controller"
        return name

    @staticmethod
    def generate_class_name(controller_name: str) -> str:
        """Generate class name from controller file name.

        Args:
            controller_name: The controller file name (with or without _controller suffix)

        Returns:
            Properly formatted class name
        """
        # Remove _controller suffix if present
        base_name = controller_name.replace("_controller", "")

        # Split by underscore and capitalize each word
        words = base_name.split("_")
        class_name = "".join(word.capitalize() for word in words)

        return f"{class_name}Controller"
