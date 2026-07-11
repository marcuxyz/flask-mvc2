from collections import namedtuple

from .namespace_middleware import NamespaceMiddleware

Model = namedtuple("Model", "method path controller action")


class RouterMiddleware:
    """
    RouterMiddleware class for managing routes in a web application.

    This class provides methods to define and manage different HTTP routes
    (GET, POST, PUT, DELETE) for the application's controllers and actions.

    Attributes:
        ROUTES (list): A class-level list that stores all the routes registered
                       with their respective HTTP methods, paths, controllers,
                       and actions.

    Methods:
        _method_route(): Private method that organizes routes by HTTP method.

        namespace(name: str): Static method to create a namespace for routes.

        get(path: str, resource: str): Static method to define a GET route.

        post(path: str, resource: str): Static method to define a POST route.

        put(path: str, resource: str): Static method to define a PUT route.

        delete(path: str, resource: str): Static method to define a DELETE route.

        all(resource: str, only=None, base_path=""): Static method to define routes for all
                                                     standard RESTful actions for a resource.

        _add_routes(name, actions, base_path): Private method to add routes for specified
                                               actions under a given name and base path.
    """

    ROUTES = []

    @staticmethod
    def _method_route():
        """
        Organizes routes by HTTP method.

        Returns:
            dict: A dictionary where each key is an HTTP method and the value is a list
                  of routes associated with that method.
        """

        routes = {}

        for route in RouterMiddleware.ROUTES:
            value = list(route.values())[0]
            for key in route:
                if key not in routes:
                    routes[key] = [value]
                else:
                    routes[key].append(value)
        return routes

    @staticmethod
    def namespace(name: str):
        """
        Creates a namespace middleware for routes.

        Args:
            name (str): The name of the namespace.

        Returns:
            NamespaceMiddleware: An instance of NamespaceMiddleware associated with the given name.
        """

        return NamespaceMiddleware(name, RouterMiddleware)

    @staticmethod
    def get(path: str, resource: str):
        """
        Defines a GET route.

        Args:
            path (str): URL path for the route.
            resource (str): The 'controller#action' string specifying the controller and action.
        """

        controller, action = resource.split("#")
        RouterMiddleware.ROUTES.append(
            {controller: Model(["GET"], path, controller, action)}
        )

    @staticmethod
    def post(path: str, resource: str):
        """
        Defines a POST route.

        Args:
            path (str): URL path for the route.
            resource (str): The 'controller#action' string specifying the controller and action.
        """

        controller, action = resource.split("#")
        RouterMiddleware.ROUTES.append(
            {controller: Model(["POST"], path, controller, action)}
        )

    @staticmethod
    def put(path: str, resource: str):
        """
        Defines a PUT route.

        Args:
            path (str): URL path for the route.
            resource (str): The 'controller#action' string specifying the controller and action.
        """

        controller, action = resource.split("#")
        RouterMiddleware.ROUTES.append(
            {controller: Model(["PUT", "PATCH"], path, controller, action)},
        )

    @staticmethod
    def delete(path: str, resource: str):
        """
        Defines a DELETE route.

        Args:
            path (str): URL path for the route.
            resource (str): The 'controller#action' string specifying the controller and action.
        """

        controller, action = resource.split("#")
        RouterMiddleware.ROUTES.append(
            {controller: Model(["DELETE"], path, controller, action)}
        )

    @staticmethod
    def all(resource: str, only=None, base_path=""):
        """
        Defines routes for all standard RESTful actions for a resource.

        Args:
            resource (str): The name of the resource.
            only (str or None): A space-separated string of actions to limit the routes to.
            base_path (str): The base path to prepend to the resource path.
        """

        group = [
            "index",
            "show",
            "new",
            "create",
            "edit",
            "update",
            "delete",
        ]
        actions = only.split() if isinstance(only, str) else only
        RouterMiddleware._add_routes(resource, actions if actions else group, base_path)

    @staticmethod
    def _add_routes(name, actions, base_path):
        """
        Adds routes for specified actions under a given name and base path.

        Args:
            name (str): The name of the resource.
            actions (list): A list of actions to create routes for.
            base_path (str): The base path to prepend to the resource path.
        """

        groups = {
            "index": "get",
            "new": "get",
            "create": "post",
        }
        parameters = {
            "show": "get",
            "edit": "get",
            "update": "put",
            "delete": "delete",
        }
        urls = {
            "new": "/new",
            "edit": "/<id>/edit",
            "show": "/<id>",
            "update": "/<id>",
            "delete": "/<id>",
        }

        for action in actions:
            path = f"{base_path}/{name}{urls.get(action, '')}"

            if action in parameters:
                getattr(RouterMiddleware, parameters[action])(path, f"{name}#{action}")
                continue

            getattr(RouterMiddleware, groups[action])(path, f"{name}#{action}")
