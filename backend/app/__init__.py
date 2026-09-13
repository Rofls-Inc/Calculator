from flask import Flask
from flask_cors import CORS

from backend.app.api.calculations import calculations_bp
from backend.app.api.health import health_bp
from backend.app.api.history import history_bp
from backend.app.config import Config
from backend.app.extensions import db
from backend.app.models import Calculation


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(calculations_bp, url_prefix="/api/v1")
    app.register_blueprint(history_bp, url_prefix="/api/v1")

    # Importing Calculation above registers its table in SQLAlchemy metadata.
    # create_all is sufficient for Sprint 0; migrations can be added later.
    with app.app_context():
        db.create_all()

    return app
