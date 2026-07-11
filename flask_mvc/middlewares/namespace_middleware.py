class NamespaceMiddleware:
    """NamespaceMiddleware."""

    def __init__(self, name: str, router):
        self.name = name
        self._router = router

    def namespace(self, name: str):
        """Create a namespace.

        :param name: Name to the new namespace.
        """
        return self._router.namespace(self.name + name)

    def get(self, path: str, resource: str):
        """Add a GET router.

        :param path: Path to the new namespace.
        :param resource: Controller and action to the new namespace.
          example: 'home#index'
        """
        return self._router.get(self.name + path, resource)

    def post(self, path: str, resource: str):
        """Add a POST router.

        :param path: Path to the new namespace.
        :param resource: Controller and action to the new namespace.
          example: 'home#index'
        """
        return self._router.post(self.name + path, resource)

    def put(self, path: str, resource: str):
        """Add a PUT and PATCH router.

        :param path: Path to the new namespace.
        :param resource: Controller and action to the new namespace.
          example: 'home#index'
        """
        return self._router.put(self.name + path, resource)

    def delete(self, path: str, resource: str):
        """Add a DELETE router.

        :param path: Path to the new namespace.
        :param resource: Controller and action to the new namespace.
          example: 'home#index'
        """
        return self._router.delete(self.name + path, resource)

    def all(self, resource: str, only=None):
        """Add many routers to one resource.

        :param resource: Controller.
        :param only: Methods to br implemented.
        """
        return self._router.all(resource, only, base_path=self.name)
