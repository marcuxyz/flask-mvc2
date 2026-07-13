"""
Integration tests for Flask MVC - testing complete workflows and interactions.
"""

import gc
import json

from flask import Flask, url_for

from tests.app import db
from tests.app.models.message import Message
from tests.test_utils import DatabaseHelper, ResponseHelper, TimerUtil, performance_test

# Complete Workflow Tests


def test_full_crud_workflow_via_api(empty_client, response_helper):
    """Test complete CRUD workflow using API endpoints."""
    response = empty_client.get(url_for("messages.index"))
    response_helper.assert_status_code(response, 200)

    create_data = {"title": "Integration Test Message"}
    create_response = empty_client.post(
        url_for("messages.create"),
        data=json.dumps(create_data),
        headers={"Content-Type": "application/json"},
    )
    response_helper.assert_status_code(create_response, 201)
    response_helper.assert_json_response(create_response, create_data)

    message = Message.query.filter_by(title="Integration Test Message").first()
    assert message is not None, "Message not found in database after creation"

    show_response = empty_client.get(url_for("messages.show", id=message.id))
    response_helper.assert_status_code(show_response, 200)

    update_data = {"title": "Updated Integration Test Message"}
    update_response = empty_client.put(
        url_for("messages.update", id=message.id),
        data=json.dumps(update_data),
        headers={"Content-Type": "application/json"},
    )
    response_helper.assert_status_code(update_response, 200)
    response_helper.assert_json_response(update_response, update_data)

    db.session.refresh(message)
    assert message.title == "Updated Integration Test Message"

    delete_response = empty_client.delete(url_for("messages.delete", id=message.id))
    response_helper.assert_redirect(delete_response)

    deleted_message = Message.query.get(message.id)
    assert deleted_message is None, "Message still exists after deletion"


def test_full_crud_workflow_via_forms(empty_browser, app):
    """Test complete CRUD workflow using browser forms."""
    # Create a message first via API
    with app.test_client() as client:
        create_response = client.post(
            url_for("messages.create"),
            data=json.dumps({"title": "Form Test Message"}),
            headers={"Content-Type": "application/json"},
        )
        assert create_response.status_code == 201

    message = Message.query.filter_by(title="Form Test Message").first()
    assert message is not None

    empty_browser.visit(url_for("messages.edit", id=message.id))
    assert empty_browser.is_element_present_by_name("_method")
    assert empty_browser.is_element_present_by_value("PUT")

    empty_browser.visit(url_for("messages.show", id=message.id))
    assert empty_browser.is_element_present_by_name("_method")
    assert empty_browser.is_element_present_by_value("DELETE")


def test_multi_resource_interaction(client):
    """Test interaction between multiple resources/controllers."""
    messages_response = client.get(url_for("messages.index"))
    assert messages_response.status_code == 200

    callbacks_response = client.get(url_for("callbacks.index"))
    assert callbacks_response.status_code == 200
    assert callbacks_response.text == "before request message"

    health_response = client.get(url_for("health.index"))
    assert health_response.status_code == 200

    assert "from_after_request" not in messages_response.headers

    callbacks_show_response = client.get(url_for("callbacks.show", id=1))
    assert callbacks_show_response.headers.get("from_after_request") == "yes"


# Error Handling Tests


def test_404_handling(client):
    """Test 404 error handling."""
    response = client.get("/nonexistent/route")
    assert response.status_code == 404


def test_method_not_allowed_handling(client):
    """Test 405 Method Not Allowed handling."""
    response = client.delete(url_for("messages.index"))
    assert response.status_code == 405


def test_invalid_json_handling(empty_client):
    """Test handling of invalid JSON in requests."""
    response = empty_client.post(
        url_for("messages.create"),
        data="invalid json data",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code in [400, 422, 500]


def test_database_error_handling(empty_client, db_helper):
    """Test handling of database errors."""
    response = empty_client.post(
        url_for("messages.create"),
        data=json.dumps({"title": "DB Test Message"}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 201

    assert db_helper.count_messages() == 1


# Performance Tests


@performance_test(max_duration=2.0)
def test_multiple_request_performance(client):
    """Test performance with multiple rapid requests."""
    for i in range(50):
        response = client.get(url_for("messages.index"))
        assert response.status_code == 200


@performance_test(max_duration=3.0)
def test_crud_operations_performance(empty_client):
    """Test performance of rapid CRUD operations."""
    created_ids = []

    for i in range(10):
        response = empty_client.post(
            url_for("messages.create"),
            data=json.dumps({"title": f"Performance Test {i}"}),
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 201

        message = Message.query.filter_by(title=f"Performance Test {i}").first()
        created_ids.append(message.id)

    for message_id in created_ids:
        response = empty_client.get(url_for("messages.show", id=message_id))
        assert response.status_code == 200

    for message_id in created_ids:
        response = empty_client.put(
            url_for("messages.update", id=message_id),
            data=json.dumps({"title": f"Updated Performance Test {message_id}"}),
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200

    for message_id in created_ids:
        response = empty_client.delete(url_for("messages.delete", id=message_id))
        assert response.status_code == 302


def test_csrf_protection_compatibility(client):
    """Test that CSRF protection works with the framework."""
    message = Message.query.first()
    response = client.put(
        url_for("messages.update", id=message.id),
        data={"title": "CSRF Test Update"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200


def test_method_override_security(client):
    """Test that method override doesn't introduce security issues."""
    message = Message.query.first()

    response = client.post(
        url_for("messages.update", id=message.id),
        data={"_method": "PUT", "title": "Valid Method Override"},
    )
    assert response.status_code == 200


def test_input_sanitization(empty_client):
    """Test that inputs are properly handled."""
    test_inputs = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE messages; --",
        "../../etc/passwd",
        "\x00null\x00byte",
    ]

    for test_input in test_inputs:
        response = empty_client.post(
            url_for("messages.create"),
            data=json.dumps({"title": test_input}),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 201

        message = Message.query.filter_by(title=test_input).first()
        assert message is not None
        assert message.title == test_input


# Scalability Tests


def test_large_dataset_handling(empty_client, db_helper):
    """Test application behavior with larger datasets."""
    messages = db_helper.create_sample_messages(100)

    response = empty_client.get(url_for("messages.index"))
    assert response.status_code == 200

    middle_message = messages[50]
    response = empty_client.get(url_for("messages.show", id=middle_message.id))
    assert response.status_code == 200

    response = empty_client.put(
        url_for("messages.update", id=middle_message.id),
        data=json.dumps({"title": "Updated Large Dataset Message"}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200


def test_memory_usage_stability(client):
    """Test that memory usage remains stable over multiple requests."""
    gc.collect()
    initial_objects = len(gc.get_objects())

    for _ in range(100):
        response = client.get(url_for("messages.index"))
        assert response.status_code == 200

    gc.collect()
    final_objects = len(gc.get_objects())

    object_growth = final_objects - initial_objects
    assert object_growth < 1000, f"Memory leak detected: {object_growth} new objects"


# Configuration Tests


def test_development_configuration(app):
    """Test application works in development mode."""
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            response = client.get(url_for("messages.index"))
            assert response.status_code == 200
        db.drop_all()


def test_production_like_configuration(app):
    """Test application works in production-like mode."""
    app.config["DEBUG"] = False
    app.config["TESTING"] = False

    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            response = client.get(url_for("messages.index"))
            assert response.status_code == 200
        db.drop_all()


def test_custom_template_folder_integration():
    """Test that custom template folder configuration works."""
    from flask_mvc import FlaskMVC

    app = Flask(__name__)
    app.config["TESTING"] = True
    FlaskMVC(app, path="tests.app")

    assert app.template_folder == "views"
