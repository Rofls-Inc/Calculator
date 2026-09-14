import uuid
from flask import Blueprint, jsonify, make_response, request
from backend.app.services.calculator import evaluate_expression, ExpressionError
from backend.app.models.calculation import Calculation
from backend.app.extensions import db


calculations_bp = Blueprint("calculations", __name__)

USER_ID_COOKIE = "user_id"

EVAL_ERROR_CODE = "EVAL_ERROR"
EVAL_ERROR_MESSAGE = "Invalid expression"
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

    user_id = request.cookies.get(USER_ID_COOKIE)
    set_cookie = False
    if not user_id:
        user_id = str(uuid.uuid4())
        set_cookie = True

    try:
        value = evaluate_expression(expression)
    except ExpressionError:
        save_calculation(
            user_id=user_id,
            expression=str(expression) if expression is not None else "",
            result="Error",
        )
        resp = make_response(
            jsonify({"error": {"code": EVAL_ERROR_CODE,
                               "message": EVAL_ERROR_MESSAGE}}),
            400,
        )
    else:
        save_calculation(
            user_id=user_id,
            expression=expression,
            result=str(value),
        )
        resp = make_response(jsonify({"result": value}), 200)

    if set_cookie:
        resp.set_cookie(
            USER_ID_COOKIE,
            user_id,
            httponly=True,
            secure=False,    
            samesite="Lax",
        )
    return resp
