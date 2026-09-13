from sqlalchemy import select

from backend.app.extensions import db
from backend.app.models import Calculation


def add_calculation(
    user_id: str,
    expression: str,
    result: str,
) -> Calculation:
    if not user_id:
        raise ValueError("user_id must not be empty")

    calculation = Calculation(
        user_id=user_id,
        expression=expression,
        result=result,
    )
    db.session.add(calculation)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return calculation


def list_calculations(user_id: str) -> list[Calculation]:
    if not user_id:
        return []

    statement = (
        select(Calculation)
        .where(Calculation.user_id == user_id)
        .order_by(Calculation.created_at.desc(), Calculation.id.desc())
    )
    return list(db.session.scalars(statement).all())
