"""Rotas no estilo Rails: ``Router.get("/", "home#index")``, ``Router.all("posts")``."""

from typing import NamedTuple


class Route(NamedTuple):
    methods: list[str]
    path: str
    controller: str
    action: str


# action -> (HTTP methods, URL suffix). One table instead of three dictionaries.
REST = {
    "index": (["GET"], ""),
    "show": (["GET"], "/<id>"),
    "new": (["GET"], "/new"),
    "create": (["POST"], ""),
    "edit": (["GET"], "/<id>/edit"),
    "update": (["PUT", "PATCH"], "/<id>"),
    "delete": (["DELETE"], "/<id>"),
}


def controller_class_name(controller: str) -> str:
    """'api_v1_users' -> 'ApiV1UsersController'.

    Single source of truth for the convention: the loader and CLI generator use this function.
    """
    return "".join(part.capitalize() for part in controller.split("_")) + "Controller"


class Scope:
    """A URL prefix and a list of routes. ``Router`` is the root scope (empty prefix)."""

    def __init__(self, prefix: str = "", routes: list[Route] | None = None):
        self.prefix = prefix
        self.routes = [] if routes is None else routes

    def namespace(self, name: str) -> "Scope":
        return Scope(self.prefix + name, self.routes)

    def get(self, path: str, resource: str) -> None:
        self._add(["GET"], path, resource)

    def post(self, path: str, resource: str) -> None:
        self._add(["POST"], path, resource)

    def put(self, path: str, resource: str) -> None:
        self._add(["PUT", "PATCH"], path, resource)

    def delete(self, path: str, resource: str) -> None:
        self._add(["DELETE"], path, resource)

    def all(self, resource: str, only: str | list[str] | None = None) -> None:
        actions = only.split() if isinstance(only, str) else (only or list(REST))
        for action in actions:
            if action not in REST:
                raise ValueError(f"Unknown action {action!r}; use one of {list(REST)}")
            methods, suffix = REST[action]
            self._add(methods, f"/{resource}{suffix}", f"{resource}#{action}")

    def _add(self, methods: list[str], path: str, resource: str) -> None:
        controller, _, action = resource.partition("#")
        if not controller or not action:
            raise ValueError(f"Expected 'controller#action', got {resource!r}")
        self.routes.append(Route(methods, self.prefix + path, controller, action))


Router = Scope()
