"""``flask mvc generate controller <name>``"""

import re
from pathlib import Path

import click
from flask import current_app
from flask.cli import AppGroup
from jinja2 import Environment, PackageLoader

from .router import controller_class_name

mvc = AppGroup("mvc", help="Flask MVC commands.")


@mvc.group()
def generate():
    """Generate MVC components."""


@generate.command()
@click.argument("name")
@click.option(
    "--path", "-p", help="Where to create it (default: <app path>/controllers)."
)
@click.option("--force", "-f", is_flag=True, help="Overwrite an existing controller.")
def controller(name: str, path: str | None, force: bool) -> None:
    """Generate a controller with the seven RESTful actions.

    \b
    flask mvc generate controller home
    flask mvc generate controller api_v1_user --path custom/controllers
    """
    if not re.fullmatch(r"[a-zA-Z]\w*", name):
        raise click.BadParameter(
            "must start with a letter and contain only letters, numbers and underscores",
            param_hint="NAME",
        )

    resource = name.removesuffix("_controller")
    app_package = current_app.extensions["mvc"]["path"]  # "app", "src", "tests.app"...
    directory = Path(path) if path else Path(*app_package.split("."), "controllers")
    target = directory / f"{resource}_controller.py"

    if target.exists() and not force:
        raise click.ClickException(f"{target} already exists. Use --force to overwrite.")

    # Autoescape is disabled because the generated output is Python code, not HTML.
    env = Environment(  # nosec B701
        loader=PackageLoader("flask_mvc", "templates"),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    code = env.get_template("controller.py.jinja2").render(
        resource=resource, class_name=controller_class_name(resource)
    )

    directory.mkdir(parents=True, exist_ok=True)
    target.write_text(code, encoding="utf-8")

    click.secho(f"✓ Controller created at {target}", fg="green")
    click.echo(
        f"Next: add `Router.all({resource!r})` to routes.py and create views/{resource}/."
    )
