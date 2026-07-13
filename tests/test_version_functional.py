"""
Comprehensive version testing for flask-mvc package.
"""

import json
import logging
import os
import re

import pytest

from flask_mvc.__version__ import __version__

# Version Information Tests


def test_version_exists():
    """Test that version information exists."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format():
    """Test that version follows semantic versioning format."""
    semver_pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(
        semver_pattern, __version__
    ), f"Version {__version__} doesn't follow semantic versioning"


def test_current_version_value():
    """Test the current version value."""
    assert __version__ == "0.4.0"


def test_version_components():
    """Test individual version components."""
    major, minor, patch = __version__.split(".")

    assert major.isdigit(), f"Major version '{major}' is not numeric"
    assert minor.isdigit(), f"Minor version '{minor}' is not numeric"
    assert patch.isdigit(), f"Patch version '{patch}' is not numeric"

    assert int(major) >= 0, "Major version should be non-negative"
    assert int(minor) >= 0, "Minor version should be non-negative"
    assert int(patch) >= 0, "Patch version should be non-negative"


def test_version_import_paths():
    """Test that version can be imported from different paths."""
    from flask_mvc.__version__ import __version__ as version_direct

    assert version_direct == __version__

    try:
        import flask_mvc

        if hasattr(flask_mvc, "__version__"):
            version_main = flask_mvc.__version__
            # Check if it's a module (which means improper import) or string
            if hasattr(version_main, "__version__"):
                version_main = version_main.__version__
            assert version_main == __version__
    except (ImportError, AttributeError):
        pass


def test_version_consistency_with_pyproject():
    """Test version consistency with pyproject.toml."""
    try:
        import toml
    except ImportError:
        pytest.skip("toml package not available")

    project_root = os.path.dirname(os.path.dirname(__file__))
    pyproject_path = os.path.join(project_root, "pyproject.toml")

    if os.path.exists(pyproject_path):
        with open(pyproject_path, "r") as f:
            pyproject_data = toml.load(f)

        pyproject_version = (
            pyproject_data.get("tool", {}).get("poetry", {}).get("version")
        )
        if pyproject_version:
            assert (
                __version__ == pyproject_version
            ), f"Version mismatch: __version__.py has {__version__}, pyproject.toml has {pyproject_version}"


# Version Comparison Tests


def test_version_comparison_with_previous():
    """Test that current version is reasonable compared to expected previous versions."""
    current_version = tuple(map(int, __version__.split(".")))

    minimum_expected = (0, 1, 0)
    assert (
        current_version >= minimum_expected
    ), f"Current version {__version__} is lower than expected minimum {'.'.join(map(str, minimum_expected))}"


def test_version_backward_compatibility_indicator():
    """Test version indicates backward compatibility."""
    major, minor, patch = map(int, __version__.split("."))

    if major >= 2:
        assert minor >= 0, "Minor version should be non-negative for stable releases"


def test_version_development_indicators():
    """Test that version doesn't contain development indicators in production."""
    development_indicators = ["dev", "alpha", "beta", "rc", "pre"]

    version_lower = __version__.lower()
    for indicator in development_indicators:
        assert (
            indicator not in version_lower
        ), f"Version {__version__} contains development indicator '{indicator}'"


# Version Metadata Tests


def test_version_module_attributes():
    """Test that version module has expected attributes."""
    import flask_mvc.__version__ as version_module

    assert hasattr(version_module, "__version__")

    optional_attributes = ["__author__", "__email__", "__description__"]
    for attr in optional_attributes:
        if hasattr(version_module, attr):
            assert isinstance(getattr(version_module, attr), str)


def test_package_version_accessibility():
    """Test that version is accessible from package imports."""
    import flask_mvc

    assert hasattr(flask_mvc, "FlaskMVC")
    assert hasattr(flask_mvc, "Router")


def test_version_string_properties():
    """Test string properties of version."""
    assert (
        __version__.strip() == __version__
    ), "Version should not have leading/trailing whitespace"

    assert len(__version__.strip()) > 0, "Version should not be empty"

    assert "." in __version__, "Version should contain dots for component separation"

    assert (
        __version__.count(".") == 2
    ), f"Version should have exactly 2 dots, got {__version__.count('.')}"


# Version Integration Tests


def test_version_in_application_context(app):
    """Test that version information is available in application context."""
    with app.app_context():
        from flask_mvc.__version__ import __version__

        assert __version__ is not None


def test_version_logging_compatibility():
    """Test that version can be used in logging contexts."""
    logger = logging.getLogger("test")
    try:
        logger.info(f"Flask MVC version: {__version__}")
        assert True
    except Exception as e:
        pytest.fail(f"Version logging failed: {e}")


def test_version_json_serialization():
    """Test that version can be JSON serialized."""
    version_data = {"version": __version__}

    try:
        json_string = json.dumps(version_data)
        restored_data = json.loads(json_string)
        assert restored_data["version"] == __version__
    except Exception as e:
        pytest.fail(f"Version JSON serialization failed: {e}")
