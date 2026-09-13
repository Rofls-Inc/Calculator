from flask import Blueprint, jsonify


calculations_bp = Blueprint("calculations", __name__)


@calculations_bp.post("/calculate")
def calculate():
    """Calculate an expression. Student 1 implements this endpoint."""
    return jsonify({"error": "Calculation endpoint is not implemented yet"}), 501
