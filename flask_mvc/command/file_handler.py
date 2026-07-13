"""File system utilities for Flask MVC CLI."""

from pathlib import Path
from typing import Optional

from .exceptions import ControllerGenerationError


class FileHandler:
    """Handles file system operations for code generation."""

    @staticmethod
    def ensure_directory_exists(directory_path: Path) -> None:
        """Create directory if it doesn't exist.

        Args:
            directory_path: Path to the directory to create
        """
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ControllerGenerationError(
                f"Failed to create directory {directory_path}: {e}"
            ) from e

    @staticmethod
    def file_exists(file_path: Path) -> bool:
        """Check if file exists.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file exists, False otherwise
        """
        return file_path.exists()

    @staticmethod
    def write_file(file_path: Path, content: str) -> None:
        """Write content to file.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file

        Raises:
            ControllerGenerationError: If file writing fails
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise ControllerGenerationError(
                f"Failed to write file {file_path}: {e}"
            ) from e
