"""
Tests for the method-override helper and the {{ method() }} template function.
"""

import time

import markupsafe
import pytest
from flask import render_template_string, url_for

from flask_mvc.extension import hidden_method
from tests.app.models.message import Message

# hidden_method


@pytest.mark.parametrize("verb", ["put", "PUT", "Put"])
def test_hidden_method_put_is_case_insensitive(verb):
    assert str(hidden_method(verb)) == "<input type='hidden' name='_method' value=PUT>"


def test_hidden_method_delete():
    assert (
        str(hidden_method("delete"))
        == "<input type='hidden' name='_method' value=DELETE>"
    )


def test_hidden_method_patch():
    """Regression: the documentation promised PATCH, but the previous version raised KeyError."""
    assert (
        str(hidden_method("PATCH")) == "<input type='hidden' name='_method' value=PATCH>"
    )


def test_hidden_method_rejects_other_verbs():
    with pytest.raises(ValueError):
        hidden_method("get")


def test_hidden_method_is_markup():
    assert isinstance(hidden_method("put"), markupsafe.Markup)


def test_patch_override_reaches_update_action(client):
    message = Message.query.first()
    response = client.post(
        url_for("messages.update", id=message.id),
        data={"_method": "PATCH", "title": "patched"},
    )
    assert response.status_code == 200
    assert Message.query.get(message.id).title == "patched"


def test_put_input_hidden_in_edit_form(browser):
    """Test that PUT hidden input is present in edit forms."""
    message = Message.query.filter_by(title="Message One").first()
    browser.visit(url_for("messages.edit", id=message.id))

    assert browser.is_element_present_by_name("_method")
    assert browser.is_element_present_by_value("PUT")

    method_input = browser.find_by_name("_method").first
    assert method_input["type"] == "hidden"


def test_delete_input_hidden_in_show_form(browser):
    """Test that DELETE hidden input is present in show forms."""
    message = Message.query.filter_by(title="Message One").first()
    browser.visit(url_for("messages.show", id=message.id))

    assert browser.is_element_present_by_name("_method")
    assert browser.is_element_present_by_value("DELETE")

    method_input = browser.find_by_name("_method").first
    assert method_input["type"] == "hidden"


def test_method_override_template_function(client):
    """Test that method function is available in templates."""
    message = Message.query.first()
    response = client.get(url_for("messages.edit", id=message.id))

    assert response.status_code == 200


def test_method_override_middleware_configuration(app):
    """Test that method override middleware is properly configured."""
    from method_override.wsgi_method_override import MethodOverrideMiddleware

    assert isinstance(app.wsgi_app, MethodOverrideMiddleware)


# Form Method Override Tests


def test_put_method_override_in_update(browser):
    """Test that PUT method override works for updates."""
    message = Message.query.filter_by(title="Message One").first()
    original_title = message.title

    browser.visit(url_for("messages.edit", id=message.id))

    browser.fill("title", "Updated via PUT override")
    browser.find_by_value("send").click()

    from tests.app import db

    db.session.refresh(message)
    assert message.title == "Updated via PUT override"
    assert message.title != original_title


def test_delete_method_override_in_destroy(browser):
    """Test that DELETE method override works for deletion."""
    message = Message.query.filter_by(title="Message One").first()
    message_id = message.id

    browser.visit(url_for("messages.show", id=message.id))

    browser.find_by_value("delete").click()

    assert browser.url.endswith("/messages")

    deleted_message = Message.query.get(message_id)
    assert deleted_message is None


def test_form_without_method_override(browser):
    """Test that forms without method override work normally."""
    browser.visit(url_for("messages.index"))
    assert browser.status_code.code == 200


# Edge Cases Tests


def test_invalid_method_override_value(client):
    """Test form submission with invalid method override value."""
    message = Message.query.first()

    response = client.post(
        url_for("messages.update", id=message.id),
        data={"_method": "INVALID", "title": "Should not update"},
    )

    assert response.status_code in [200, 400, 405]


def test_missing_method_override_value(client):
    """Test form submission with empty method override."""
    message = Message.query.first()

    response = client.post(
        url_for("messages.update", id=message.id),
        data={"_method": "", "title": "Empty method override"},
    )

    assert response.status_code in [200, 400, 405]


def test_method_override_with_get_request(client):
    """Test that method override doesn't affect GET requests."""
    message = Message.query.first()

    response = client.get(
        url_for("messages.show", id=message.id), query_string={"_method": "DELETE"}
    )

    assert response.status_code == 200


# Template Helper Integration Tests


def test_helper_function_injection(app):
    """Test that helper functions are properly injected into templates."""
    with app.app_context():
        context_processors = app.template_context_processors[None]
        assert len(context_processors) > 0

        context = {}
        for processor in context_processors:
            context.update(processor())

        assert "method" in context
        assert callable(context["method"])


def test_helper_function_in_template_context(client):
    """Test that helper function works correctly in template context."""
    with client.application.test_request_context():
        template = """
        {{ method('put') }}
        {{ method('delete') }}
        """

        result = render_template_string(template)

        assert "<input type='hidden' name='_method' value=PUT>" in result
        assert "<input type='hidden' name='_method' value=DELETE>" in result


def test_multiple_helper_calls_in_template(client):
    """Test multiple helper function calls in same template."""
    with client.application.test_request_context():
        template = """
        <form method="post">
            {{ method('put') }}
            <input type="text" name="title">
        </form>
        <form method="post">
            {{ method('delete') }}
            <input type="submit" value="Delete">
        </form>
        """

        result = render_template_string(template)

        assert result.count("_method") == 2
        assert "value=PUT" in result
        assert "value=DELETE" in result


def test_helper_function_performance():
    start = time.time()
    for _ in range(1000):
        hidden_method("put")
        hidden_method("delete")
    assert time.time() - start < 1.0
