"""Тесты HTTP-эндпоинта GET /api/v1/history и разделения истории по клиентам"""

import re

import pytest

from tests.conftest import COOKIE_NAME, calculate, history_items


ISO_WITH_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")


def test_new_client_gets_empty_history(client):
    response = client.get("/api/v1/history")

    assert response.status_code == 200
    assert response.get_json() == {"items": []}


def test_new_client_receives_cookie(client):
    response = client.get("/api/v1/history")

    assert COOKIE_NAME in response.headers.get("Set-Cookie", "")


def test_history_item_matches_contract(client):
    calculate(client, "2+2")

    item = history_items(client)[0]
    assert set(item) == {"id", "expression", "result", "created_at"}
    assert item["expression"] == "2+2"
    assert ISO_WITH_Z.match(item["created_at"]), item["created_at"]


def test_history_is_sorted_newest_first(client):
    for expression in ("1+1", "2+2", "3+3"):
        calculate(client, expression)

    expressions = [item["expression"] for item in history_items(client)]
    assert expressions == ["3+3", "2+2", "1+1"]


def test_history_survives_many_entries(client):
    for index in range(20):
        calculate(client, f"{index}+1")

    items = history_items(client)
    assert len(items) == 20
    assert items[0]["expression"] == "19+1"


# разделение по клиентам

def test_two_clients_have_separate_histories(client, other_client):
    """Два браузера на одном сервере не видят вычисления друг друга"""
    calculate(client, "2+2")
    calculate(other_client, "3+3")

    assert [item["expression"] for item in history_items(client)] == ["2+2"]
    assert [item["expression"] for item in history_items(other_client)] == ["3+3"]


def test_client_without_cookie_sees_nothing_of_others(client, other_client):
    calculate(client, "2+2")

    assert history_items(other_client) == []


def test_cookie_identifies_the_client(app, client):
    """Второй браузер с тем же cookie видит ту же историю"""
    calculate(client, "2+2")
    cookie_value = client.get_cookie(COOKIE_NAME).value

    impersonator = app.test_client()
    impersonator.set_cookie(COOKIE_NAME, cookie_value)

    assert [item["expression"] for item in history_items(impersonator)] == ["2+2"]


@pytest.mark.parametrize("cookie_value", ["not-a-uuid", "", "../../etc/passwd",
                                          "1 OR 1=1", "x" * 500])
def test_broken_cookie_does_not_crash(crash_safe_client, cookie_value):
    """Подделанный cookie не должен ломать сервер и не должен давать чужую историю"""
    crash_safe_client.set_cookie(COOKIE_NAME, cookie_value)

    response = crash_safe_client.get("/api/v1/history")

    assert response.status_code == 200
    assert response.get_json()["items"] == []


# сохранность между запусками

def test_history_survives_restart(app_factory):
    """История лежит в файле SQLite и переживает перезапуск backend"""
    first_app = app_factory()
    first_client = first_app.test_client()
    calculate(first_client, "2+2")
    cookie_value = first_client.get_cookie(COOKIE_NAME).value

    restarted_app = app_factory()
    restarted_client = restarted_app.test_client()
    restarted_client.set_cookie(COOKIE_NAME, cookie_value)

    items = history_items(restarted_client)
    assert [item["expression"] for item in items] == ["2+2"]
