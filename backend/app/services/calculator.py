class ExpressionError(ValueError):
    """Raised when an arithmetic expression is invalid or unsupported."""


def evaluate_expression(expression: str) -> int | float:
    """Evaluate a safe arithmetic expression.

    Student 1 implements tokenization/parsing here. Raw Python eval must not be
    used because the API accepts untrusted input.
    """
    raise NotImplementedError("Expression evaluator is not implemented yet")
