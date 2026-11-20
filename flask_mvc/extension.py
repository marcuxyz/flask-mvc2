"""FlaskMVC: the complete extension.

``init_app`` flow: routes.py -> controllers -> blueprints -> app
"""

import sys
from collections import defaultdict
from importlib import import_module, reload

from flask import Blueprint, Flask, request
from markupsafe import Markup
from method_override.wsgi_method_override import MethodOverrideMiddleware

from .cli import mvc
from .router import Route, Router, controller_class_name


class FlaskMVCError(Exception):
    pass


class RoutesModuleNotFoundError(FlaskMVCError):
    pass


class FlaskMVC:
    def __init__(self, app: Flask | None = None, path: str = "app", db=None):
        if app is not None:
            self.init_app(app, path, db)

    def init_app(self, app: Flask, path: str = "app", db=None) -> None:
        """``path`` is the application package in import notation (e.g. ``"app"``)."""
        app.extensions["mvc"] = {"path": path}
        app.template_folder = "views"
        app.wsgi_app = MethodOverrideMiddleware(app.wsgi_app)
        app.context_processor(lambda: {"method": hidden_method})
        app.cli.add_command(mvc)

        for blueprint in _blueprints(path):
            app.register_blueprint(blueprint)

        if db is not None:  # after controllers: they import the models
            _reflect(app, db)


def hidden_method(verb: str) -> Markup:
    """``{{ method('PUT') }}`` -> input hidden lido pelo MethodOverrideMiddleware."""
    verb = verb.upper()
    if verb not in ("PUT", "PATCH", "DELETE"):
        raise ValueError(f"method() accepts PUT, PATCH or DELETE, got {verb!r}")
    return Markup(f"<input type='hidden' name='_method' value={verb}>")  # nosec B704


def _load_routes(path: str) -> list[Route]:
    """Execute ``<path>/routes.py``, which populates ``Router`` as a side effect."""
    module = f"{path}.routes"
    Router.routes.clear()  # init_app may run multiple times (tests, multiple apps)
    try:
        if module in sys.modules:
            reload(sys.modules[module])
        else:
            import_module(module)
    except ModuleNotFoundError as error:
        # Translate only when routes (or its package) is missing; re-raise broken imports inside it unchanged.
        if error.name and (module == error.name or module.startswith(error.name + ".")):
            raise RoutesModuleNotFoundError(
                f"routes.py doesn't exist. Create the {module.replace('.', '/')}.py file."
            ) from None
        raise
    return list(Router.routes)


def _blueprints(path: str) -> list[Blueprint]:
    """One blueprint per controller: ``home#index`` -> ``<path>.controllers.home_controller``."""
    by_controller: dict[str, list[Route]] = defaultdict(list)
    for route in _load_routes(path):
        by_controller[route.controller].append(route)

    blueprints = []
    for name, routes in by_controller.items():
        module = import_module(f"{path}.controllers.{name}_controller")
        controller = getattr(module, controller_class_name(name))()

        blueprint = Blueprint(name, __name__)
        for route in routes:
            blueprint.add_url_rule(
                route.path,
                endpoint=route.action,
                view_func=getattr(controller, route.action),
                methods=route.methods,
            )
        _bind_callbacks(blueprint, controller)
        blueprints.append(blueprint)
    return blueprints


def _bind_callbacks(blueprint: Blueprint, controller) -> None:
    """``before_request = dict(callback="hi", actions="index show")`` becomes a blueprint hook."""
    for hook in ("before_request", "after_request"):
        spec = getattr(controller, hook, None)
        if spec is None:
            continue
        callback = getattr(controller, spec["callback"])
        endpoints = {f"{blueprint.name}.{action}" for action in spec["actions"].split()}

        def run(*args, callback=callback, endpoints=endpoints):
            if request.endpoint in endpoints:
                callback(*args)
            return args[0] if args else None  # after_request must return the response

        getattr(blueprint, hook)(run)


def _reflect(app: Flask, db) -> None:
    from sqlalchemy.exc import InvalidRequestError, OperationalError

    from .model import BaseModel

    with app.app_context():
        try:
            BaseModel.prepare(db.engine)
        except (OperationalError, InvalidRequestError):
            app.logger.info(
                "[flask_mvc] deferred reflection: database or tables do not exist yet."
            )
