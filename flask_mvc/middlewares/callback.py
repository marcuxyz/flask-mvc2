from flask import Flask, request


class Callback:
    def __init__(self, app: Flask, controller_name: str, controller) -> None:
        """
        Initializes the CallbackMiddleware instance.

        Parameters:
        app (Flask): The Flask application where the middleware is being registered.
        controller_name (str): The name of the controller where the hooks are defined.
        controller: The controller instance where the hooks are defined.
        """
        self.app = app
        self.controller_name = controller_name
        self.controller = controller

    def register(self):
        """
        Registers before_request and after_request hooks to the Flask application.
        The before_request hook is executed before the request is processed.
        The after_request hook is executed after the request is processed.

        The hooks are retrieved using the get_hook_method function and executed using the execute_hook function.
        """

        def before_request_hook():
            hook_method, actions = self.get_hook_method("before_request")
            if hook_method:
                self.execute_hook(hook_method, actions)

        def after_request_hook(response):
            hook_method, actions = self.get_hook_method("after_request")
            if hook_method:
                self.execute_hook(hook_method, actions, response)
            return response

        self.app.before_request_funcs.setdefault(None, []).append(before_request_hook)
        self.app.after_request_funcs.setdefault(None, []).append(after_request_hook)

    def get_hook_method(self, hook_name):
        """
        Retrieves the hook method associated with the given hook name from the controller.

        Parameters:
        hook_name (str): The name of the hook method to retrieve.

        Returns:
        tuple: A tuple containing the callback method associated with the hook and the actions to be performed.
            If the hook does not exist, returns (False, False).
        """
        if hasattr(self.controller, hook_name):
            hook_attribute = getattr(self.controller, hook_name)
            callback = hook_attribute["callback"]
            actions = self.actions(hook_attribute)

            return getattr(self.controller, callback), actions

        return False, False

    def execute_hook(self, hook_method, actions, response=None):
        """
        Executes the specified hook method for each action in the provided list of actions
        if the current request endpoint matches the controller and action name.

        Parameters:
        hook_method (function): The hook method to be executed.
        actions (list): A list of action names.
        response (flask.Response, optional): The response object to be passed to the hook method. Defaults to None.
        """
        for action in actions:
            endpoint = f"{self.controller_name}.{action}"
            if request.endpoint == endpoint:
                if response is None:
                    hook_method()
                else:
                    hook_method(response)

    def actions(self, values):
        """
        Splits the actions string from the given values dictionary into a list of individual actions.

        Parameters:
        values (dict): A dictionary containing an "actions" key whose value is a string of action names separated by spaces.

        Returns:
        list: A list of individual action names.
        """
        return values["actions"].split()
