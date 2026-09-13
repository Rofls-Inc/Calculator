from flask import Blueprint, jsonify


history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
def history():
    """Return the current client's history. Student 2 implements this endpoint."""
    return jsonify({"error": "History endpoint is not implemented yet"}), 501
