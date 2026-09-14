"""Тесты слоя данных: модель Calculation и repository истории"""

import pytest

from backend.app.models import Calculation
from backend.app.repositories import add_calculation, list_calculations


@pytest.fixture()
def db_context(app):
    """Контекст приложения с готовой базой"""
    with app.app_context():
        yield


def test_add_calculation_returns_saved_row(db_context):
    row = add_calculation(user_id="user-1", expression="2+2", result="4")

    assert row.id is not None
    assert row.created_at is not None


def test_add_calculation_requires_user_id(db_context):
    with pytest.raises(ValueError):
        add_calculation(user_id="", expression="2+2", result="4")


def test_list_returns_only_own_rows(db_context):
    add_calculation(user_id="user-1", expression="1+1", result="2")
    add_calculation(user_id="user-2", expression="3+3", result="6")

    rows = list_calculations("user-1")

    assert [row.expression for row in rows] == ["1+1"]


def test_list_is_sorted_newest_first(db_context):
    """Записи одной секунды различаются по id - порядок должен быть стабильным"""
    for expression in ("1+1", "2+2", "3+3"):
        add_calculation(user_id="user-1", expression=expression, result="x")

    rows = list_calculations("user-1")

    assert [row.expression for row in rows] == ["3+3", "2+2", "1+1"]


def test_list_for_unknown_user_is_empty(db_context):
    add_calculation(user_id="user-1", expression="1+1", result="2")

    assert list_calculations("user-2") == []


def test_list_for_empty_user_id_is_empty(db_context):
    add_calculation(user_id="user-1", expression="1+1", result="2")

    assert list_calculations("") == []


def test_to_dict_matches_api_contract(db_context):
    add_calculation(user_id="user-1", expression="2+2", result="4")

    payload = list_calculations("user-1")[0].to_dict()

    assert set(payload) == {"id", "expression", "result", "created_at"}
    assert "user_id" not in payload, "идентификатор клиента наружу не отдаётся"
    assert payload["created_at"].endswith("Z")


def test_expression_at_max_length_is_stored(db_context):
    """Колонка expression рассчитана на 512 символов"""
    expression = "1+" * 255 + "11"
    assert len(expression) == 512

    add_calculation(user_id="user-1", expression=expression, result="512")

    assert list_calculations("user-1")[0].expression == expression


def test_rows_are_isolated_per_user(db_context):
    for index in range(5):
        add_calculation(user_id="user-1", expression=f"{index}+1", result="x")
    add_calculation(user_id="user-2", expression="9+9", result="18")

    assert len(list_calculations("user-1")) == 5
    assert len(list_calculations("user-2")) == 1
    assert Calculation.query.count() == 6
