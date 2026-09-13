import pytest

from backend.app import create_app


@pytest.fixture()
def app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
