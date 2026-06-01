from typing import Any

from flask import Flask, redirect, url_for

from frontend.api import get_service_status
from frontend.auth import current_user
from frontend.settings import DJANGO_API_URL, NOTIFICATION_API_URL, UGC_API_URL


def register_layout_helpers(app: Flask) -> None:
    @app.context_processor
    def inject_layout_context() -> dict[str, Any]:
        return {
            "current_user": current_user(),
            "service_statuses": {
                "django": get_service_status(f"{DJANGO_API_URL}/api/shop/products/"),
                "ugc": get_service_status(f"{UGC_API_URL}/api/ugc/health/"),
                "notifications": get_service_status(f"{NOTIFICATION_API_URL}/api/notifications/health/"),
            },
        }

    @app.route("/")
    def index():
        return redirect(url_for("products"))
