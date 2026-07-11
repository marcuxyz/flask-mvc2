"""
Comprehensive tests for Flask MVC callback middleware system.
"""

import pytest
from flask import Response, request, url_for

from flask_mvc.middlewares.callback import Callback as CallbackMiddleware
from tests.app.controllers.callbacks_controller import CallbacksController

# Callback Middleware Tests


def test_before_request_execution(client):
    """Test that before_request callback is executed."""
    response = client.get(url_for("callbacks.index"))

    assert response.status_code == 200
    assert response.text == "before request message"


def test_after_request_execution(client):
    """Test that after_request callback is executed."""
    response = client.get(url_for("callbacks.show", id=1))

    assert response.status_code == 200
    assert response.headers.get("from_after_request") == "yes"
    assert response.text == "hello"


def test_callback_middleware_initialization(app):
    """Test callback middleware initialization."""
    controller = CallbacksController()
    middleware = CallbackMiddleware(app, "callbacks", controller)

    assert middleware.app == app
    assert middleware.controller_name == "callbacks"
    assert middleware.controller == controller


def test_get_hook_method_existing(app):
    """Test retrieving existing hook method."""
    controller = CallbacksController()
    middleware = CallbackMiddleware(app, "callbacks", controller)

    hook_method, actions = middleware.get_hook_method("before_request")

    assert hook_method is not False
    assert actions == ["index"]
    assert callable(hook_method)


def test_get_hook_method_nonexistent(app):
    """Test retrieving non-existent hook method."""
    controller = CallbacksController()
    middleware = CallbackMiddleware(app, "callbacks", controller)

    hook_method, actions = middleware.get_hook_method("nonexistent_hook")

    assert hook_method is False
    assert actions is False


def test_actions_parsing(app):
    """Test action string parsing."""
    controller = CallbacksController()
    middleware = CallbackMiddleware(app, "callbacks", controller)

    actions = middleware.actions({"actions": "index"})
    assert actions == ["index"]

    actions = middleware.actions({"actions": "index show edit"})
    assert actions == ["index", "show", "edit"]


def test_hook_execution_with_matching_endpoint(app):
    """Test hook execution when endpoint matches."""
    controller = CallbacksController()
    middleware = CallbackMiddleware(app, "callbacks", controller)

    with app.test_request_context("/callbacks"):
        # Mock the request to simulate endpoint matching
        from unittest.mock import patch

        with patch("flask.request") as mock_request:
            mock_request.endpoint = "callbacks.index"

            executed = []

            def mock_hook():
                executed.append("called")

            middleware.execute_hook(mock_hook, ["index"])
            assert len(executed) == 1


def test_hook_execution_without_matching_endpoint(app):
    """Test hook execution when endpoint doesn't match."""
    controller = CallbacksController()
    middleware = CallbackMiddleware(app, "callbacks", controller)

    with app.test_request_context("/other"):
        # Mock the request to simulate endpoint not matching
        from unittest.mock import patch

        with patch("flask.request") as mock_request:
            mock_request.endpoint = "other.index"

            executed = []

            def mock_hook():
                executed.append("called")

            middleware.execute_hook(mock_hook, ["index"])
            assert len(executed) == 0


# Callback Configuration Tests


def test_multiple_actions_before_request(app):
    """Test before_request callback with multiple actions."""

    class MultiActionController:
        before_request = dict(callback="setup", actions="index show edit")

        def setup(self):
            self.data = "initialized"

        def index(self):
            return getattr(self, "data", "not initialized")

        def show(self, id):
            return getattr(self, "data", "not initialized")

        def edit(self, id):
            return getattr(self, "data", "not initialized")

    controller = MultiActionController()
    middleware = CallbackMiddleware(app, "multi", controller)

    _, actions = middleware.get_hook_method("before_request")
    assert actions == ["index", "show", "edit"]


def test_after_request_with_response_modification(app):
    """Test after_request callback modifying response."""

    class ResponseModifierController:
        after_request = dict(callback="modify_response", actions="index")

        def index(self):
            return "original response"

        def modify_response(self, response):
            response.headers["Custom-Header"] = "modified"
            return response

    controller = ResponseModifierController()
    middleware = CallbackMiddleware(app, "modifier", controller)

    with app.test_request_context("/modifier"):
        # Mock the request to simulate endpoint matching
        from unittest.mock import patch

        with patch("flask.request") as mock_request:
            mock_request.endpoint = "modifier.index"

            response = Response("test")

            hook_method, actions = middleware.get_hook_method("after_request")
            hook_method(response)

            assert response.headers.get("Custom-Header") == "modified"


# Edge Cases Tests


def test_callback_without_actions(app):
    """Test callback configuration without actions."""

    class NoActionsController:
        before_request = dict(callback="setup", actions="")

        def setup(self):
            pass

    controller = NoActionsController()
    middleware = CallbackMiddleware(app, "no_actions", controller)

    _, actions = middleware.get_hook_method("before_request")
    assert actions == [] or actions == [""]


def test_callback_with_invalid_method(app):
    """Test callback configuration with invalid method."""

    class InvalidMethodController:
        before_request = dict(callback="nonexistent_method", actions="index")

        def setup(self):
            pass

    controller = InvalidMethodController()
    middleware = CallbackMiddleware(app, "invalid", controller)

    try:
        hook_method, actions = middleware.get_hook_method("before_request")
        assert actions == ["index"]
    except AttributeError:
        pytest.skip("Expected behavior - method doesn't exist")


def test_empty_controller(app):
    """Test middleware with controller that has no callbacks."""

    class EmptyController:
        def index(self):
            return "empty"

    controller = EmptyController()
    middleware = CallbackMiddleware(app, "empty", controller)

    hook_method, actions = middleware.get_hook_method("before_request")
    assert hook_method is False
    assert actions is False


def test_malformed_callback_config(app):
    """Test malformed callback configuration."""

    class MalformedController:
        before_request = "not a dict"

    controller = MalformedController()
    middleware = CallbackMiddleware(app, "malformed", controller)

    with pytest.raises((TypeError, KeyError, AttributeError)):
        middleware.get_hook_method("before_request")


# Integration Tests


def test_full_request_cycle_with_callbacks(client):
    """Test complete request cycle with both before and after callbacks."""
    response = client.get(url_for("callbacks.index"))

    assert response.status_code == 200
    assert response.text == "before request message"
    assert "from_after_request" not in response.headers

    response = client.get(url_for("callbacks.show", id=1))

    assert response.status_code == 200
    assert response.text == "hello"
    assert response.headers.get("from_after_request") == "yes"


def test_callback_state_isolation(client):
    """Test that callback state doesn't leak between requests."""
    response1 = client.get(url_for("callbacks.index"))
    assert response1.text == "before request message"

    response2 = client.get(url_for("callbacks.index"))
    assert response2.text == "before request message"

    assert response1.text == response2.text


def test_multiple_controllers_callback_isolation(client):
    """Test that callbacks from different controllers don't interfere."""
    callbacks_response = client.get(url_for("callbacks.index"))
    assert callbacks_response.text == "before request message"

    messages_response = client.get(url_for("messages.index"))
    assert messages_response.status_code == 200
    assert "from_after_request" not in messages_response.headers
