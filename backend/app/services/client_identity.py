from uuid import UUID, uuid4

from flask import Response, current_app, request


def get_or_create_client_id() -> tuple[str, bool]:
    cookie_name = current_app.config["CLIENT_COOKIE_NAME"]
    cookie_value = request.cookies.get(cookie_name)

    if cookie_value:
        try:
            normalized_value = str(UUID(cookie_value))
            if normalized_value == cookie_value:
                return normalized_value, False
        except (ValueError, AttributeError):
            pass

    return str(uuid4()), True


def attach_client_cookie(response: Response, client_id: str) -> None:
    response.set_cookie(
        key=current_app.config["CLIENT_COOKIE_NAME"],
        value=client_id,
        max_age=current_app.config["CLIENT_COOKIE_MAX_AGE_SECONDS"],
        httponly=True,
        secure=current_app.config["CLIENT_COOKIE_SECURE"],
        samesite="Lax",
        path="/",
    )
