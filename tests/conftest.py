"""
Comprehensive test configuration with improved fixtures and utilities.
"""

import pytest
from splinter import Browser

from flask_mvc.middlewares.base_model import BaseModel
from tests.app import create_app, db
from tests.app.models.message import Message


@pytest.fixture(scope="session")
def app():
    """Create application for the tests with session scope."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "SERVER_NAME": "localhost.localdomain",
            "APPLICATION_ROOT": "/",
            "PREFERRED_URL_SCHEME": "http",
        }
    )

    return app


@pytest.fixture
def client(app):
    """Create test client with database setup."""
    with app.app_context():
        db.create_all()
        BaseModel.prepare(db.engine)

        # Create sample data
        sample_message = Message(title="Message One")
        db.session.add(sample_message)
        db.session.commit()

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
        db.drop_all()


@pytest.fixture
def empty_client(app):
    """Create test client without sample data."""
    with app.app_context():
        db.create_all()
        BaseModel.prepare(db.engine)

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
        db.drop_all()


@pytest.fixture
def browser(app):
    """Create browser for integration testing."""
    with app.app_context():
        db.create_all()
        BaseModel.prepare(db.engine)

        # Create sample data
        sample_message = Message(title="Message One")
        db.session.add(sample_message)
        db.session.commit()

        browser = Browser("flask", app=app)
        yield browser
        browser.quit()

        db.session.remove()
        db.drop_all()


@pytest.fixture
def empty_browser(app):
    """Create browser without sample data."""
    with app.app_context():
        db.create_all()
        BaseModel.prepare(db.engine)
        browser = Browser("flask", app=app)
        yield browser
        browser.quit()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_messages(app):
    """Create multiple sample messages for testing."""
    with app.app_context():
        db.create_all()
        BaseModel.prepare(db.engine)

        messages = [
            Message(title="First Message"),
            Message(title="Second Message"),
            Message(title="Third Message"),
        ]

        for message in messages:
            db.session.add(message)
        db.session.commit()

        yield messages

        # Cleanup
        for message in messages:
            db.session.delete(message)
        db.session.commit()


# Helper class fixtures from test_utils.py
@pytest.fixture
def db_helper():
    """Database helper for tests."""
    from tests.test_utils import DatabaseHelper

    return DatabaseHelper()


@pytest.fixture
def response_helper():
    """Response helper for tests."""
    from tests.test_utils import ResponseHelper

    return ResponseHelper()


@pytest.fixture
def route_helper():
    """Route helper for tests."""
    from tests.test_utils import RouteHelper

    return RouteHelper()


@pytest.fixture
def validation_helper():
    """Validation helper for tests."""
    from tests.test_utils import ValidationHelper

    return ValidationHelper()


@pytest.fixture
def benchmark_helper():
    """Benchmark helper for tests."""
    from tests.test_utils import BenchmarkHelper

    return BenchmarkHelper()
