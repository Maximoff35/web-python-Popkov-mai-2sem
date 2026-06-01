from flask import Flask, flash, redirect, render_template, request, url_for

from frontend.api import ApiError, api_request
from frontend.auth import auth_headers, login_required
from frontend.settings import DJANGO_API_URL


def register_order_routes(app: Flask) -> None:
    @app.route("/orders", methods=["GET"])
    @login_required
    def orders():
        selected_order = None
        orders_data = []
        try:
            response_data = api_request(
                "GET",
                f"{DJANGO_API_URL}/api/shop/orders/",
                headers=auth_headers(),
            )
            if isinstance(response_data, dict) and "results" in response_data:
                orders_data = response_data.get("results", [])
            elif isinstance(response_data, list):
                orders_data = response_data
            else:
                flash("Неожиданный формат ответа сервера.", "error")
            order_id = request.args.get("order_id")
            if order_id:
                selected_order = api_request(
                    "GET",
                    f"{DJANGO_API_URL}/api/shop/orders/{int(order_id)}/",
                    headers=auth_headers(),
                )
        except (ApiError, ValueError) as error:
            flash(error.message if isinstance(error, ApiError) else "Некорректный id заказа", "error")
            orders_data = []
        selected_order_items = selected_order.get("items", []) if selected_order else []
        return render_template(
            "orders.html",
            orders=orders_data,
            selected_order=selected_order,
            selected_order_items=selected_order_items,
        )

    @app.route("/orders/create", methods=["POST"])
    @login_required
    def create_order():
        try:
            result = api_request(
                "POST",
                f"{DJANGO_API_URL}/api/shop/orders/create/",
                headers=auth_headers(),
                expected_statuses=(201,),
            )
            flash(
                f"Заказ #{result['order_id']} создан",
                "success",
            )
            return redirect(url_for("orders", order_id=result["order_id"]))
        except ApiError as error:
            flash(error.message, "error")
            return redirect(url_for("cart"))
