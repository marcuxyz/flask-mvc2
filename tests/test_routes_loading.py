"""
Tests for how FlaskMVC finds and loads <path>/routes.py.
"""

import pytest
from flask import Flask

from flask_mvc import FlaskMVC
from flask_mvc.extension import RoutesModuleNotFoundError


def test_missing_routes_module_has_a_clear_error(tmp_path, monkeypatch):
    (tmp_path / "no_routes_app").mkdir()
    (tmp_path / "no_routes_app" / "__init__.py").write_text("")
    monkeypatch.syspath_prepend(str(tmp_path))

    with pytest.raises(RoutesModuleNotFoundError, match="routes.py doesn't exist"):
        FlaskMVC(Flask(__name__), path="no_routes_app")


def test_broken_import_inside_routes_is_not_reported_as_missing_routes(
    tmp_path, monkeypatch
):
    """A ModuleNotFoundError raised inside routes.py must be propagated unchanged."""
    package = tmp_path / "broken_routes_app"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "routes.py").write_text("import a_dependency_that_does_not_exist\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    with pytest.raises(ModuleNotFoundError, match="a_dependency_that_does_not_exist"):
        FlaskMVC(Flask(__name__), path="broken_routes_app")
