from flask import Blueprint, jsonify, make_response, request

from backend.app.repositories import add_calculation
from backend.app.services.calculator import ExpressionError, evaluate_expression
from backend.app.services.client_identity import attach_client_cookie, get_or_create_client_id

calculations_bp = Blueprint("calculations", __name__)

EVAL_ERROR_CODE = "INVALID_EXPRESSION"
EVAL_ERROR_MESSAGE = "Expression contains a syntax error"
JSON_REQUIRED_CODE = "JSON_REQUIRED"
JSON_REQUIRED_MESSAGE = "Request must be JSON"


@calculations_bp.post("/calculate")
def calculate():
    if not request.is_json:
        return jsonify({"error": {"code": JSON_REQUIRED_CODE,
                                  "message": JSON_REQUIRED_MESSAGE}}), 400

    body = request.get_json(silent=True) or {}
    expression = body.get("expression")

    client_id, is_new_client = get_or_create_client_id()

    try:
        value = evaluate_expression(expression)
    except ExpressionError:
        resp = make_response(
            jsonify({"error": {"code": EVAL_ERROR_CODE,
                               "message": EVAL_ERROR_MESSAGE}}),
            400,
        )
    else:
        add_calculation(
            user_id=client_id,
            expression=expression,
            result=str(value),
        )
        resp = make_response(jsonify({"result": str(value)}), 200)

    if is_new_client:
        attach_client_cookie(resp, client_id)

    return resp
