from sqlalchemy.sql import func

from backend.app.extensions import db


class Calculation(db.Model):
    """A successful calculation stored for one anonymous browser client."""

    __tablename__ = "calculations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    expression = db.Column(db.String(512), nullable=False)
    result = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Calculation {self.expression} = {self.result}>"
