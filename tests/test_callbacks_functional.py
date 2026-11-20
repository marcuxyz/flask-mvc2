"""
Tests for controller callbacks (before_request / after_request).
"""

import pytest
from flask import Blueprint, Flask, url_for

from flask_mvc.extension import _bind_callbacks


def make_client(controller_cls, actions=("index", "show", "edit")):
    """Create a minimal app with a 'things' blueprint and bound controller hooks."""
    app = Flask(__name__)
    controller = controller_cls()
    blueprint = Blueprint("things", __name__)
    for action in actions:
        blueprint.add_url_rule(
            f"/{action}", endpoint=action, view_func=getattr(controller, action)
        )
    _bind_callbacks(blueprint, controller)
    app.register_blueprint(blueprint)
    return app.test_client()


# Comportamento dos hooks


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


def test_before_request_runs_for_every_listed_action():
    class Things:
        before_request = dict(callback="setup", actions="index show")

        def setup(self):
            self.data = "initialized"

        def index(self):
            return getattr(self, "data", "not initialized")

        show = edit = index

    client = make_client(Things)

    assert client.get("/index").text == "initialized"
    assert client.get("/show").text == "initialized"


def test_before_request_skips_unlisted_actions():
    class Things:
        before_request = dict(callback="setup", actions="index")

        def setup(self):
            self.data = "initialized"

        def index(self):
            return getattr(self, "data", "not initialized")

        show = edit = index

    client = make_client(Things, actions=("show", "index"))

    assert client.get("/show").text == "not initialized"


def test_after_request_modifies_response_only_for_listed_actions():
    class Things:
        after_request = dict(callback="stamp", actions="index")

        def stamp(self, response):
            response.headers["Custom-Header"] = "modified"

        def index(self):
            return "original"

        show = edit = index

    client = make_client(Things)

    assert client.get("/index").headers["Custom-Header"] == "modified"
    assert "Custom-Header" not in client.get("/show").headers


def test_controller_without_callbacks_is_untouched():
    class Things:
        def index(self):
            return "plain"

        show = edit = index

    assert make_client(Things).get("/index").text == "plain"


def test_missing_callback_method_fails_at_startup():
    class Things:
        before_request = dict(callback="nope", actions="index")

        def index(self):
            return ""

        show = edit = index

    with pytest.raises(AttributeError):
        make_client(Things)


def test_malformed_callback_config_fails_at_startup():
    class Things:
        before_request = "not a dict"

        def index(self):
            return ""

        show = edit = index

    with pytest.raises(TypeError):
        make_client(Things)


# Integration with the test app (real routes)


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
