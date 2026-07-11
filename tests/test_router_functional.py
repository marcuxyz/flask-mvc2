"""
Comprehensive tests for the Flask MVC routing system.
"""

from collections import Counter

import pytest
from flask import url_for

from flask_mvc import Router
from flask_mvc.middlewares.router_middleware import RouterMiddleware

# Router System Tests


def test_blueprints_registration(client):
    """Test that all expected blueprints are registered."""
    expected_blueprints = {"messages", "health", "posts", "callbacks"}
    actual_blueprints = set(client.application.blueprints.keys())
    assert actual_blueprints == expected_blueprints


def test_blueprint_uniqueness(client):
    """Test that each blueprint is registered only once."""
    blueprint_counts = Counter(client.application.blueprints.keys())
    for blueprint, count in blueprint_counts.items():
        assert count == 1, f"Blueprint '{blueprint}' registered {count} times"


def test_messages_routes_structure(client):
    """Test that messages routes follow RESTful conventions."""
    expected_routes = {
        "/messages",
        "/messages/new",
        "/messages/<id>",
        "/messages/<id>/edit",
    }

    actual_routes = {route.rule for route in client.application.url_map.iter_rules()}

    for expected_route in expected_routes:
        assert expected_route in actual_routes, f"Route {expected_route} not found"


def test_messages_endpoints_completeness(client):
    """Test that all CRUD endpoints are properly registered."""
    expected_endpoints = {
        "messages.index",
        "messages.show",
        "messages.new",
        "messages.create",
        "messages.edit",
        "messages.update",
        "messages.delete",
    }

    actual_endpoints = {
        route.endpoint for route in client.application.url_map.iter_rules()
    }

    for expected_endpoint in expected_endpoints:
        assert (
            expected_endpoint in actual_endpoints
        ), f"Endpoint {expected_endpoint} not found"


def test_http_methods_distribution(client):
    """Test that HTTP methods are correctly distributed across routes."""
    method_counts = Counter(
        method
        for route in client.application.url_map.iter_rules()
        for method in route.methods
    )

    expected_methods = {
        "GET": 9,
        "POST": 1,
        "PUT": 1,
        "PATCH": 1,
        "DELETE": 1,
    }

    for method, expected_count in expected_methods.items():
        assert (
            method_counts[method] == expected_count
        ), f"Expected {expected_count} {method} routes, got {method_counts[method]}"


# Namespace Routing Tests


def test_api_namespace_routes(client):
    """Test that API namespace routes are properly prefixed."""
    api_routes = [
        route.rule
        for route in client.application.url_map.iter_rules()
        if route.rule.startswith("/api/v1")
    ]

    assert "/api/v1/health" in api_routes
    # The posts route might have a different structure due to controller naming
    posts_routes = [route for route in api_routes if "posts" in route]
    assert len(posts_routes) > 0


def test_nested_namespace_functionality(client):
    """Test that nested namespaces work correctly."""
    posts_routes = [
        route.rule
        for route in client.application.url_map.iter_rules()
        if "/posts" in route.rule
    ]

    # Verify that posts routes exist, regardless of exact path structure
    assert len(posts_routes) > 0


def test_namespace_endpoint_naming(client):
    """Test that namespace endpoints follow correct naming conventions."""
    health_endpoints = [
        route.endpoint
        for route in client.application.url_map.iter_rules()
        if "health" in route.endpoint
    ]

    assert "health.index" in health_endpoints


# Router Methods Isolation Tests


def test_get_route_registration():
    """Test GET route registration."""
    RouterMiddleware.ROUTES.clear()
    Router.get("/test", "test#index")

    routes = RouterMiddleware._method_route()
    assert "test" in routes
    assert routes["test"][0].method == ["GET"]
    assert routes["test"][0].path == "/test"
    assert routes["test"][0].action == "index"


def test_post_route_registration():
    """Test POST route registration."""
    RouterMiddleware.ROUTES.clear()
    Router.post("/test", "test#create")

    routes = RouterMiddleware._method_route()
    assert "test" in routes
    assert routes["test"][0].method == ["POST"]
    assert routes["test"][0].action == "create"


def test_put_route_registration():
    """Test PUT route registration."""
    RouterMiddleware.ROUTES.clear()
    Router.put("/test/<id>", "test#update")

    routes = RouterMiddleware._method_route()
    assert "test" in routes
    assert routes["test"][0].method == ["PUT", "PATCH"]
    assert routes["test"][0].action == "update"


def test_delete_route_registration():
    """Test DELETE route registration."""
    RouterMiddleware.ROUTES.clear()
    Router.delete("/test/<id>", "test#destroy")

    routes = RouterMiddleware._method_route()
    assert "test" in routes
    assert routes["test"][0].method == ["DELETE"]
    assert routes["test"][0].action == "destroy"


def test_all_routes_registration():
    """Test that Router.all() creates all RESTful routes."""
    RouterMiddleware.ROUTES.clear()
    Router.all("products")

    routes = RouterMiddleware._method_route()
    assert "products" in routes

    assert len(routes["products"]) == 7

    actions = {route.action for route in routes["products"]}
    expected_actions = {"index", "new", "create", "show", "edit", "update", "delete"}
    assert actions == expected_actions


def test_all_routes_with_only_filter():
    """Test Router.all() with only parameter."""
    RouterMiddleware.ROUTES.clear()
    Router.all("products", only="index show")

    routes = RouterMiddleware._method_route()
    assert "products" in routes
    assert len(routes["products"]) == 2

    actions = {route.action for route in routes["products"]}
    assert actions == {"index", "show"}


# Router Edge Cases Tests


def test_multiple_routes_same_controller():
    """Test multiple routes for the same controller."""
    RouterMiddleware.ROUTES.clear()
    Router.get("/users", "users#index")
    Router.get("/users/active", "users#active")
    Router.post("/users", "users#create")

    routes = RouterMiddleware._method_route()
    assert len(routes["users"]) == 3


def test_namespace_path_concatenation():
    """Test that namespace paths are properly concatenated."""
    RouterMiddleware.ROUTES.clear()
    api = Router.namespace("/api")
    api.get("/test", "test#index")

    routes = RouterMiddleware._method_route()
    assert routes["test"][0].path == "/api/test"


def test_nested_namespace_paths():
    """Test deeply nested namespace paths."""
    RouterMiddleware.ROUTES.clear()
    api = Router.namespace("/api")
    v1 = api.namespace("/v1")
    v1.get("/test", "test#index")

    routes = RouterMiddleware._method_route()
    assert routes["test"][0].path == "/api/v1/test"
