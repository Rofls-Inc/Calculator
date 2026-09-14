import pytest

from backend.app import create_app


COOKIE_NAME = "calculator_user_id"


@pytest.fixture()
def app():
    """Приложение на базе в памяти"""
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    yield application


@pytest.fixture()
def client(app):
    """Браузер пользователя: у каждого test_client свой набор cookie"""
    return app.test_client()


@pytest.fixture()
def other_client(app):
    """Второй браузер на том же сервере"""
    return app.test_client()


@pytest.fixture()
def crash_safe_client(app):
    app.config["PROPAGATE_EXCEPTIONS"] = False
    return app.test_client()


@pytest.fixture()
def app_factory(tmp_path):
    db_path = tmp_path / "calculator.db"

    def _create():
        return create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            }
        )

    return _create


def calculate(test_client, expression):
    """Короткий помощник: POST /api/v1/calculate с корректным JSON"""
    return test_client.post("/api/v1/calculate", json={"expression": expression})


def history_items(test_client):
    """Короткий помощник: список записей из GET /api/v1/history"""
    response = test_client.get("/api/v1/history")
    assert response.status_code == 200
    return response.get_json()["items"]
