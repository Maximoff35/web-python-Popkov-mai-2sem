from flask import Flask, flash, redirect, render_template, request, url_for

from frontend.api import ApiError, api_request
from frontend.auth import auth_headers, login_required
from frontend.settings import DJANGO_API_URL


def register_cart_routes(app: Flask) -> None:
    @app.route("/cart")
    @login_required
    def cart():
        try:
            cart_data = api_request(
                "GET",
                f"{DJANGO_API_URL}/api/shop/cart/",
                headers=auth_headers(),
            )
        except ApiError as error:
            flash(error.message, "error")
            cart_data = {"items": []}

        items = cart_data.get("items", [])
        total = sum(float(item["price"]) * item["quantity"] for item in items)
        return render_template("cart.html", cart_items=items, total=total)

    @app.route("/cart/items/<int:item_id>/quantity", methods=["POST"])
    @login_required
    def update_cart_item(item_id: int):
        action = request.form.get("action", "set")
        try:
            current_quantity = int(request.form.get("current_quantity", "1"))
            quantity = int(request.form.get("quantity", str(current_quantity)))
        except ValueError:
            quantity = 1
            current_quantity = 1

        if action == "increase":
            quantity = current_quantity + 1
        elif action == "decrease":
            quantity = max(1, current_quantity - 1)
        else:
            quantity = max(1, quantity)

        try:
            api_request(
                "PATCH",
                f"{DJANGO_API_URL}/api/shop/cart/items/{item_id}/",
                json={"quantity": quantity},
                headers=auth_headers(),
            )
            flash("Количество обновлено", "success")
        except ApiError as error:
            flash(error.message, "error")
        return redirect(url_for("cart"))

    @app.route("/cart/items/<int:item_id>/delete", methods=["POST"])
    @login_required
    def delete_cart_item(item_id: int):
        try:
            api_request(
                "DELETE",
                f"{DJANGO_API_URL}/api/shop/cart/items/{item_id}/",
                headers=auth_headers(),
            )
            flash("Товар удалён из корзины", "success")
        except ApiError as error:
            flash(error.message, "error")
        return redirect(url_for("cart"))
