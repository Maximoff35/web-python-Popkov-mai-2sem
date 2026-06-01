from functools import wraps
from typing import Any

from flask import flash, redirect, session, url_for

from frontend.api import ApiError, api_request
from frontend.settings import DJANGO_API_URL


def get_access_token() -> str | None:
    return session.get("access_token")


def auth_headers() -> dict[str, str]:
    token = get_access_token()
    if not token:
        raise ApiError("Нужно войти в систему.")
    return {"Authorization": f"Bearer {token}"}


def current_user() -> dict[str, Any] | None:
    if not get_access_token():
        return None
    if "current_user" in session:
        return session["current_user"]
    try:
        user = api_request(
            "GET",
            f"{DJANGO_API_URL}/api/auth/me/",
            headers=auth_headers(),
        )
        session["current_user"] = user
        return user
    except ApiError:
        return None


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not get_access_token():
            flash("Для продолжения нужно войти в систему.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view
