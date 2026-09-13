from datetime import timezone

from sqlalchemy.sql import func

from backend.app.extensions import db


class Calculation(db.Model):

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

    def to_dict(self) -> dict:
        created_at = self.created_at
        if created_at is not None and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return {
            "id": self.id,
            "expression": self.expression,
            "result": self.result,
            "created_at": (
                created_at.isoformat().replace("+00:00", "Z")
                if created_at is not None
                else None
            ),
        }

    def __repr__(self) -> str:
        return f"<Calculation {self.expression} = {self.result}>"
