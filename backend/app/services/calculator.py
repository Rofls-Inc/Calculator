from __future__ import annotations

from dataclasses import dataclass
from typing import List


class ExpressionError(ValueError):
    """Raised when an arithmetic expression is invalid or unsupported."""


@dataclass
class Token:
    kind: str   # 'NUM' | 'OP' | 'LPAREN' | 'RPAREN' | 'EOF'
    value: str
    pos: int


def _tokenize(expression: str) -> List[Token]:
    tokens: List[Token] = []
    i, n = 0, len(expression)

    while i < n:
        ch = expression[i]

        if ch.isspace():
            i += 1
            continue

        if ch == "(":
            tokens.append(Token("LPAREN", ch, i))
            i += 1
            continue

        if ch == ")":
            tokens.append(Token("RPAREN", ch, i))
            i += 1
            continue

        if ch.isdigit() or ch == ".":
            start = i
            dots = 0
            while i < n and (expression[i].isdigit() or expression[i] == "."):
                if expression[i] == ".":
                    dots += 1
                    if dots > 1:
                        raise ExpressionError(
                            f"Некорректное число в позиции {start}"
                        )
                i += 1
            text = expression[start:i]
            if text == ".":
                raise ExpressionError(f"Ожидалось число в позиции {start}")
            tokens.append(Token("NUM", text, start))
            continue

        if ch in "+-*/":
            tokens.append(Token("OP", ch, i))
            i += 1
            continue

        raise ExpressionError(f"Недопустимый символ {ch!r} в позиции {i}")

    tokens.append(Token("EOF", "", n))
    return tokens


class _Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.idx = 0

    def _peek(self) -> Token:
        return self.tokens[self.idx]

    def _advance(self) -> Token:
        tok = self.tokens[self.idx]
        self.idx += 1
        return tok

    def _match_op(self, *ops: str) -> Token | None:
        tok = self._peek()
        if tok.kind == "OP" and tok.value in ops:
            return self._advance()
        return None

    def parse(self) -> int | float:
        value = self.expr()
        tok = self._peek()
        if tok.kind != "EOF":
            raise ExpressionError(
                f"Неверный токен {tok.value!r} в позиции {tok.pos}"
            )
        return value

    def expr(self) -> int | float:
        left = self.term()
        while True:
            op = self._match_op("+", "-")
            if op is None:
                return left
            right = self.term()
            left = left + right if op.value == "+" else left - right

    def term(self) -> int | float:
        left = self.unary()
        while True:
            op = self._match_op("*", "/")
            if op is None:
                return left
            right = self.unary()
            if op.value == "*":
                left = left * right
            else:
                if right == 0:
                    raise ExpressionError("Деление на ноль")
                left = left / right

    def unary(self) -> int | float:
        op = self._match_op("+", "-")
        if op is not None:
            value = self.unary()
            return value if op.value == "+" else -value
        return self.atom()

    def atom(self) -> int | float:
        tok = self._peek()

        if tok.kind == "NUM":
            self._advance()
            try:
                if "." in tok.value:
                    return float(tok.value)
                return int(tok.value)
            except ValueError as e:
                raise ExpressionError(
                    f"Некорректное число {tok.value!r} в позиции {tok.pos}"
                ) from e

        if tok.kind == "LPAREN":
            self._advance()
            value = self.expr()
            close = self._peek()
            if close.kind != "RPAREN":
                raise ExpressionError(
                    f"Ожидалась ')' в позиции {close.pos}, "
                    f"получено {close.value!r}"
                )
            self._advance()
            return value

        if tok.kind == "EOF":
            raise ExpressionError("Неверный конец выражения")

        raise ExpressionError(
            f"Неверный токен {tok.value!r} в позиции {tok.pos}"
        )


def evaluate_expression(expression: str) -> int | float:
    """Evaluate a safe arithmetic expression."""

    if not isinstance(expression, str):
        raise ExpressionError("Выражение должно быть строкой")
    
    if not expression.strip():
        raise ExpressionError("Пустое выражение")
    
    if len(expression) > 512:
        raise ExpressionError("Слишком длинное выражение")

    tokens = _tokenize(expression)
    try:
        return _Parser(tokens).parse()
    except RecursionError as error:
        raise ExpressionError("Слишком глубокая вложенность скобок") from error
