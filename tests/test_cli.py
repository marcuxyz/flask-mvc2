"""
Tests for `flask mvc generate controller`.
"""

import sys

import pytest
from flask import Flask

from flask_mvc import FlaskMVC
from flask_mvc.router import controller_class_name


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def generate(runner, *args):
    return runner.invoke(args=["mvc", "generate", "controller", *args])


def test_creates_controller_file(runner, tmp_path):
    result = generate(runner, "blog", "--path", str(tmp_path))

    code = (tmp_path / "blog_controller.py").read_text()
    assert result.exit_code == 0
    assert "class BlogController:" in code
    compile(code, "blog_controller.py", "exec")  # valid Python


def test_accepts_name_with_controller_suffix(runner, tmp_path):
    generate(runner, "blog_controller", "--path", str(tmp_path))

    assert (tmp_path / "blog_controller.py").exists()
    assert not (tmp_path / "blog_controller_controller.py").exists()


def test_templates_use_the_resource_name_not_home(runner, tmp_path):
    """Regression: the old template always pointed to 'home/' views."""
    generate(runner, "blog", "--path", str(tmp_path))

    code = (tmp_path / "blog_controller.py").read_text()
    assert 'render_template("blog/new.html")' in code
    assert "home/" not in code


def test_refuses_to_overwrite_without_force(runner, tmp_path):
    generate(runner, "blog", "--path", str(tmp_path))
    (tmp_path / "blog_controller.py").write_text("# my edit")

    result = generate(runner, "blog", "--path", str(tmp_path))
    assert result.exit_code != 0
    assert "already exists" in result.output
    assert (tmp_path / "blog_controller.py").read_text() == "# my edit"

    assert generate(runner, "blog", "--path", str(tmp_path), "--force").exit_code == 0
    assert "class BlogController" in (tmp_path / "blog_controller.py").read_text()


@pytest.mark.parametrize("name", ["", "1blog", "my-blog", "my blog"])
def test_rejects_invalid_names(runner, tmp_path, name):
    result = generate(runner, name, "--path", str(tmp_path))

    assert result.exit_code != 0
    assert not list(tmp_path.iterdir())


def test_default_directory_follows_the_app_path(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the test app uses path="tests.app"

    generate(runner, "blog")

    assert (tmp_path / "tests" / "app" / "controllers" / "blog_controller.py").exists()


@pytest.mark.parametrize(
    "resource, expected",
    [("home", "HomeController"), ("api_v1_user", "ApiV1UserController")],
)
def test_class_name_convention(resource, expected):
    assert controller_class_name(resource) == expected


def test_generated_multiword_controller_is_loadable(tmp_path, monkeypatch):
    """Regression: the CLI generated ApiV1UserController, but the loader looked for Api_V1_UserController."""
    package = tmp_path / "rt_app"
    (package / "controllers").mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "controllers" / "__init__.py").write_text("")
    (package / "routes.py").write_text(
        "from flask_mvc import Router\n"
    )  # no routes yet
    monkeypatch.syspath_prepend(str(tmp_path))
    app = Flask(__name__)
    FlaskMVC(app, path="rt_app")  # registers the command and reads the path

    result = app.test_cli_runner().invoke(
        args=[
            "mvc",
            "generate",
            "controller",
            "api_v1_user",
            "--path",
            str(package / "controllers"),
        ]
    )
    assert result.exit_code == 0, result.output

    # Real flow: generate the controller, THEN declare the route.
    (package / "routes.py").write_text(
        "from flask_mvc import Router\nRouter.get('/ping', 'api_v1_user#index')\n"
    )
    app2 = Flask(__name__)
    FlaskMVC(app2, path="rt_app")
    response = app2.test_client().get("/ping")
    assert response.text == "Hello from ApiV1UserController!"

    for name in [m for m in sys.modules if m.startswith("rt_app")]:
        del sys.modules[name]
