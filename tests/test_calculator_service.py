"""Модульные тесты вычислителя - backend/app/services/calculator.py"""

import pytest

from backend.app.services.calculator import ExpressionError, evaluate_expression


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2+2", 4),
        ("2 + 2", 4),
        ("10-3-2", 5),
        ("2+3*4", 14),
        ("(2+3)*4", 20),
        ("2*(3+(4-1))", 12),
        ("10/4", 2.5),
        ("2.5*2", 5.0),
        ("0.1+0.4", 0.5),
        ("-5+3", -2),
        ("-(2+3)", -5),
        ("3*-2", -6),
        ("100", 100),
    ],
)
def test_valid_expressions(expression, expected):
    assert evaluate_expression(expression) == pytest.approx(expected)


def test_example_from_assignment():
    expression = "(12 + 22 * 7) / (33 + (12 * 3 - 8)) * 3"

    assert evaluate_expression(expression) == pytest.approx(8.163934426229508)



@pytest.mark.parametrize(
    "expression",
    [
        "",
        "   ",
        "2+",
        "+",
        "*5",
        "(1+2",
        "1+2)",
        "()",
        "2..3",
        ".",
        "1 2",
        "2+*3",
        "2**3",
        "2^3",
        "1,5+2",
        "1e3",
        "0x10",
        "abc",
        "два плюс два",
        "2 + 2 🙂",
    ],
)
def test_invalid_expressions_raise(expression):
    with pytest.raises(ExpressionError):
        evaluate_expression(expression)


@pytest.mark.parametrize("expression", [None, 5, 2.5, [], {}, True])
def test_non_string_input_raises(expression):
    with pytest.raises(ExpressionError):
        evaluate_expression(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('ls')",
        "open('/etc/passwd').read()",
        "1; print('hacked')",
        "eval('2+2')",
        "os.getcwd()",
        "lambda: 1",
        "[x for x in range(3)]",
        "'a'*10",
    ],
)
def test_python_code_is_rejected(expression):
    """Через API нельзя выполнить код: разрешена только арифметика"""
    with pytest.raises(ExpressionError):
        evaluate_expression(expression)


# деление на ноль

@pytest.mark.parametrize(
    "expression",
    ["1/0", "1/0.0", "1/(2-2)", "5/(3-3)*2", "(4+4)/(1-1)"],
)
def test_division_by_zero_raises(expression):
    """Деление на ноль обрабатывается, а не приводит к ZeroDivisionError."""
    with pytest.raises(ExpressionError):
        evaluate_expression(expression)


# устойчивость

def test_long_chain_of_unary_signs():
    """Длинная цепочка унарных знаков не должна ломать рекурсию"""
    assert evaluate_expression("-" * 400 + "1") == 1


def test_long_flat_expression():
    """Длинное плоское выражение в пределах лимита считается корректно"""
    assert evaluate_expression("1+" * 200 + "1") == 201


@pytest.mark.xfail(
    strict=True,
    reason="BUG-1: глубокая вложенность скобок даёт RecursionError вместо ExpressionError",
)
def test_deeply_nested_parentheses_raise_expression_error():
    """Вложенность 249 - это 499 символов, то есть в пределах лимита 512"""
    expression = "(" * 249 + "1" + ")" * 249

    with pytest.raises(ExpressionError):
        evaluate_expression(expression)
