from flask import Blueprint, jsonify

from backend.app.repositories import list_calculations
from backend.app.services.client_identity import (
    attach_client_cookie,
    get_or_create_client_id,
)


history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
def history():
    client_id, is_new_client = get_or_create_client_id()
    calculations = list_calculations(client_id)
    response = jsonify({"items": [item.to_dict() for item in calculations]})

    if is_new_client:
        attach_client_cookie(response, client_id)

    return response, 200
