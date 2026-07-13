"""Unit tests for name utilities."""

import pytest

from flask_mvc.commands.exceptions import InvalidControllerNameError
from flask_mvc.commands.name_utils import NameUtils


class TestNameUtils:
    """Test cases for NameUtils class."""

    def test_validate_controller_name_valid(self):
        """Test validation with valid controller names."""
        # These should not raise exceptions
        NameUtils.validate_controller_name("home")
        NameUtils.validate_controller_name("user_profile")
        NameUtils.validate_controller_name("API_v1")
        NameUtils.validate_controller_name("home_controller")

    def test_validate_controller_name_invalid_empty(self):
        """Test validation with empty name."""
        with pytest.raises(InvalidControllerNameError):
            NameUtils.validate_controller_name("")

    def test_validate_controller_name_invalid_start_with_number(self):
        """Test validation with name starting with number."""
        with pytest.raises(InvalidControllerNameError):
            NameUtils.validate_controller_name("1home")

    def test_validate_controller_name_invalid_special_chars(self):
        """Test validation with special characters."""
        with pytest.raises(InvalidControllerNameError):
            NameUtils.validate_controller_name("home-controller")

        with pytest.raises(InvalidControllerNameError):
            NameUtils.validate_controller_name("home@controller")

    def test_normalize_controller_name_without_suffix(self):
        """Test normalization of name without _controller suffix."""
        result = NameUtils.normalize_controller_name("home")
        assert result == "home_controller"

    def test_normalize_controller_name_with_suffix(self):
        """Test normalization of name with _controller suffix."""
        result = NameUtils.normalize_controller_name("home_controller")
        assert result == "home_controller"

    def test_generate_class_name_simple(self):
        """Test class name generation for simple names."""
        result = NameUtils.generate_class_name("home")
        assert result == "HomeController"

    def test_generate_class_name_with_underscores(self):
        """Test class name generation for names with underscores."""
        result = NameUtils.generate_class_name("user_profile")
        assert result == "UserProfileController"

    def test_generate_class_name_with_controller_suffix(self):
        """Test class name generation for names with _controller suffix."""
        result = NameUtils.generate_class_name("home_controller")
        assert result == "HomeController"

    def test_generate_class_name_complex(self):
        """Test class name generation for complex names."""
        result = NameUtils.generate_class_name("api_v1_user_profile_controller")
        assert result == "ApiV1UserProfileController"
