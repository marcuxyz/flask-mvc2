from flask import Flask
from method_override.wsgi_method_override import MethodOverrideMiddleware

from . import cli
from .middlewares.html_input_method_helper import HTMLInputMethodHelper
from .middlewares.blueprint_binding import BlueprintBinding
from .middlewares.router_middleware import RouterMiddleware as Router


class FlaskMVC:
    def __init__(self, app: Flask = None, path="app"):
        if app is not None:
            self.init_app(app, path)

    def init_app(self, app: Flask = None, path="app"):
        self.perform(app, path)

    def perform(self, app: Flask, path: str):
        self._configure_template_folder(app)
        self._configure_method_override_middleware(app)
        self._configure_blueprint_middleware(app, path)
        self._inject_object_in_jinja_template(app)
        self._configure_cli_commands(app)

    def _configure_template_folder(self, app):
        app.template_folder = "views"

    def _configure_method_override_middleware(self, app):
        app.wsgi_app = MethodOverrideMiddleware(app.wsgi_app)

    def _configure_blueprint_middleware(self, app, path):
        BlueprintBinding(app, path).register()

    def _inject_object_in_jinja_template(self, app):
        @app.context_processor
        def inject_stage_and_region():
            return {
                "method": HTMLInputMethodHelper().input_hidden_method,
            }

    def _configure_cli_commands(self, app):
        """Register CLI commands with the Flask app."""
        cli.init_app(app)
