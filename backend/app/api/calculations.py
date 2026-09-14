import uuid
from flask import Blueprint, jsonify, make_response, request
from backend.app.services.calculator import evaluate_expression, ExpressionError
from backend.app.models.calculation import Calculation
from backend.app.extensions import db
from backend.app.services.client_identity import get_or_create_client_id, attach_client_cookie



calculations_bp = Blueprint("calculations", __name__)

USER_ID_COOKIE = "user_id"

EVAL_ERROR_CODE = "INVALID_EXPRESSION"
EVAL_ERROR_MESSAGE = "Expression contains a syntax error"
JSON_REQUIRED_CODE = "JSON_REQUIRED"
JSON_REQUIRED_MESSAGE = "Request must be JSON"


def save_calculation(*, user_id: str, expression: str, result: str):
    row = Calculation(user_id=user_id, expression=expression, result=result)
    db.session.add(row)
    db.session.commit()
    return row


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
        save_calculation(
            user_id=client_id,
            expression=expression,
            result=str(value),
        )
        resp = make_response(jsonify({"result": value}), 200)

    if is_new_client:
        attach_client_cookie(resp, client_id)

    return resp
