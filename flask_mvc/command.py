"""Flask MVC CLI commands for generating MVC components.

This module provides command-line tools for scaffolding MVC components
following Flask and Python best practices.
"""

import logging

import click
from flask.cli import with_appcontext

from .commands.config import CLIConfig
from .commands.exceptions import (
    ControllerGenerationError,
    InvalidControllerNameError,
)
from .commands.controller.generator import Generator as ControllerGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def mvc():
    """Flask MVC commands."""
    pass


@mvc.group()
def generate():
    """Generate MVC components."""
    pass


@generate.command()
@click.argument("name")
@click.option(
    "--path",
    "-p",
    default=CLIConfig.DEFAULT_CONTROLLERS_PATH,
    help="Path where to create the controller",
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing controller file")
@with_appcontext
def controller(name: str, path: str, force: bool) -> None:
    """Generate a new controller.

    Creates a new controller class with RESTful methods following Flask MVC patterns.
    The controller will include standard CRUD operations and proper type hints.

    Examples:
        \b
        flask mvc generate controller home
        flask mvc generate controller user --path custom/controllers
        flask mvc generate controller api_v1_user --force
    """
    try:
        logger.info(f"Generating controller '{name}' at path '{path}'")

        generator = ControllerGenerator()
        controller_file = generator.generate(name, path, force=force)

        click.echo(
            click.style(
                f"✓ Controller created successfully at {controller_file}",
                fg=CLIConfig.SUCCESS_COLOR,
            )
        )

        # Provide helpful next steps
        controller_name = name if name.endswith("_controller") else f"{name}_controller"
        click.echo(click.style("\nNext steps:", fg=CLIConfig.INFO_COLOR, bold=True))
        click.echo(
            click.style(
                "1. Add routes for your controller in your routes.py file",
                fg=CLIConfig.INFO_COLOR,
            )
        )
        click.echo(
            click.style(
                f"2. Create templates in views/{name}/ directory",
                fg=CLIConfig.INFO_COLOR,
            )
        )
        click.echo(
            click.style(
                f"3. Implement your business logic in {controller_name}.py",
                fg=CLIConfig.INFO_COLOR,
            )
        )

    except (ControllerGenerationError, InvalidControllerNameError) as e:
        logger.error(f"Controller generation failed: {e}")
        click.echo(click.style(f"✗ Error: {e}", fg=CLIConfig.ERROR_COLOR), err=True)
        raise click.Abort() from e
    except Exception as e:
        logger.exception(f"Unexpected error during controller generation: {e}")
        click.echo(
            click.style(
                f"✗ Unexpected error: {e}. Please check the logs for more details.",
                fg=CLIConfig.ERROR_COLOR,
            ),
            err=True,
        )
        raise click.Abort() from e


def init_app(app) -> None:
    """Initialize CLI commands with Flask app.

    Args:
        app: Flask application instance
    """
    app.cli.add_command(mvc)
