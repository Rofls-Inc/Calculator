"""Тесты HTTP-эндпоинта POST /api/v1/calculate."""

import pytest

from tests.conftest import COOKIE_NAME, calculate, history_items


MAX_EXPRESSION_LENGTH = 512


def error_body(response):
    """Достаёт блок error и проверяет, что он соответствует требованиям"""
    body = response.get_json()
    assert "error" in body, f"ожидался блок error, получено {body}"
    assert body["error"].get("code"), "код ошибки обязателен"
    assert body["error"].get("message"), "сообщение об ошибке обязательно"
    return body["error"]


# успешный расчёт

def test_example_from_assignment_returns_result(client):
    response = calculate(client, "(12 + 22 * 7) / (33 + (12 * 3 - 8)) * 3")

    assert response.status_code == 200
    body = response.get_json()
    assert "error" not in body
    assert float(body["result"]) == pytest.approx(8.163934426229508)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [("2+2", 4), ("(2+3)*4", 20), ("-5+3", -2), ("10/4", 2.5)],
)
def test_valid_expressions_return_200(client, expression, expected):
    response = calculate(client, expression)

    assert response.status_code == 200
    assert float(response.get_json()["result"]) == pytest.approx(expected)


@pytest.mark.xfail(
    strict=True,
    reason="BUG-2: docs/api.md описывает result строкой, эндпоинт отдаёт число",
)
def test_result_is_a_string_per_api_contract(client):
    response = calculate(client, "2+2")

    assert isinstance(response.get_json()["result"], str)


@pytest.mark.xfail(
    strict=True,
    reason="BUG-2: /calculate отдаёт число, /history - строку; типы должны совпадать",
)
def test_result_type_matches_history(client):
    calculated = calculate(client, "6/3").get_json()["result"]
    stored = history_items(client)[0]["result"]

    assert type(calculated) is type(stored)


# некорректный ввод

@pytest.mark.parametrize(
    "expression",
    [
        "",
        "   ",
        "2+",
        "(1+2",
        "1+2)",
        "()",
        "2..3",
        "1 2",
        "2**3",
        "abc",
        "два плюс два",
        "__import__('os').system('ls')",
        "1; print('hacked')",
    ],
)
def test_invalid_expression_returns_400(client, expression):
    response = calculate(client, expression)

    assert response.status_code == 400
    error_body(response)


@pytest.mark.parametrize("expression", ["1/0", "1/(2-2)", "5/(3-3)*2"])
def test_division_by_zero_returns_400(client, expression):
    """Деление на ноль возвращает ту же структуру ошибки, что и синтаксическая"""
    response = calculate(client, expression)

    assert response.status_code == 400
    error_body(response)


@pytest.mark.parametrize("payload", [{}, {"expression": None}, {"expression": 5},
                                     {"expression": ["2+2"]}, {"expr": "2+2"}])
def test_malformed_payload_returns_400(client, payload):
    response = client.post("/api/v1/calculate", json=payload)

    assert response.status_code == 400
    error_body(response)


def test_request_without_json_content_type_returns_400(client):
    response = client.post("/api/v1/calculate", data='{"expression": "2+2"}')

    assert response.status_code == 400
    error_body(response)


def test_broken_json_returns_400(client):
    response = client.post(
        "/api/v1/calculate",
        data="{not json",
        content_type="application/json",
    )

    assert response.status_code == 400
    error_body(response)


# лимит длины

def test_expression_over_limit_returns_400(client):
    response = calculate(client, "1+" * 300 + "1")

    assert response.status_code == 400
    error_body(response)


def test_expression_just_under_limit_is_accepted(client):
    expression = "1+" * ((MAX_EXPRESSION_LENGTH - 2) // 2) + "1"
    assert len(expression) == MAX_EXPRESSION_LENGTH - 1

    assert calculate(client, expression).status_code == 200


@pytest.mark.xfail(
    strict=True,
    reason="BUG-3: проверка len >= 512 отсекает ровно 512, контракт разрешает 512",
)
def test_expression_at_exact_limit_is_accepted(client):
    expression = "1+" * ((MAX_EXPRESSION_LENGTH - 2) // 2) + "11"
    assert len(expression) == MAX_EXPRESSION_LENGTH

    assert calculate(client, expression).status_code == 200


def test_expression_over_limit_is_rejected_by_length_not_by_parsing(client):
    """Слишком длинное выражение отклоняется, даже если оно верное"""
    expression = "1+" * 400 + "1"
    assert len(expression) > MAX_EXPRESSION_LENGTH

    assert calculate(client, expression).status_code == 400


# устойчивость сервера

@pytest.mark.parametrize(
    "expression",
    [
        "a" * 5000,
        "(" * 1000 + ")" * 1000,
        "\x00\x01\x02",
        "\n\n\n",
        "🙂" * 100,
        "1/" * 300,
    ],
)
def test_garbage_input_does_not_crash_server(crash_safe_client, expression):
    """На мусорный ввод сервер отвечает 4xx и продолжает работать"""
    response = crash_safe_client.post(
        "/api/v1/calculate", json={"expression": expression}
    )

    assert response.status_code < 500
    assert crash_safe_client.get("/api/v1/health").status_code == 200


@pytest.mark.xfail(
    strict=True,
    reason="BUG-1: вложенные скобки в пределах лимита дают HTTP 500",
)
def test_deeply_nested_parentheses_return_400(crash_safe_client):
    """499 символов - в пределах лимита 512, значит отвечать должен парсер"""
    expression = "(" * 249 + "1" + ")" * 249

    response = crash_safe_client.post(
        "/api/v1/calculate", json={"expression": expression}
    )

    assert response.status_code == 400


# cookie клиента

def test_first_calculation_sets_client_cookie(client):
    """Без этого первый расчёт сохранится под id, которого нет у браузера"""
    response = calculate(client, "2+2")

    assert COOKIE_NAME in response.headers.get("Set-Cookie", "")


def test_cookie_is_not_reissued_for_known_client(client):
    calculate(client, "2+2")
    response = calculate(client, "3+3")

    assert COOKIE_NAME not in response.headers.get("Set-Cookie", "")


# связь с историей

def test_successful_calculation_is_stored(client):
    calculate(client, "2+2")

    items = history_items(client)
    assert len(items) == 1
    assert items[0]["expression"] == "2+2"


@pytest.mark.parametrize("expression", ["1/0", "(1+2", "abc"])
def test_failed_calculation_is_not_stored(client, expression):
    """Ошибочные запросы не должны попадать в историю"""
    calculate(client, expression)

    assert history_items(client) == []
