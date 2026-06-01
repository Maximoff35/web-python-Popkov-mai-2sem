from typing import Any

from flask import Flask, flash, redirect, render_template, request, url_for

from frontend.api import ApiError, api_request
from frontend.auth import auth_headers, login_required
from frontend.settings import DJANGO_API_URL, UGC_API_URL


def register_product_routes(app: Flask) -> None:
    @app.route("/products")
    def products():
        search = request.args.get("search", "").strip()
        category = request.args.get("category", "").strip()
        params: dict[str, str] = {}
        if search:
            params["search"] = search
        if category:
            params["category"] = category

        products_data: list[dict[str, Any]] = []
        error_message = None
        try:
            response_data = api_request(
                "GET",
                f"{DJANGO_API_URL}/api/shop/products/",
                params=params,
            )
            if isinstance(response_data, dict) and "results" in response_data:
                products_data = response_data.get("results", [])
            elif isinstance(response_data, list):
                products_data = response_data
            else:
                error_message = "Неожиданный формат ответа сервера."
        except ApiError as error:
            error_message = error.message

        return render_template(
            "products.html",
            products=products_data,
            filters={"search": search, "category": category},
            error_message=error_message,
        )

    @app.route("/products/<int:product_id>")
    def product_detail(product_id: int):
        try:
            product = api_request("GET", f"{DJANGO_API_URL}/api/shop/products/{product_id}/")
            reviews_response = api_request(
                "GET",
                f"{UGC_API_URL}/api/ugc/reviews/",
                params={"product_id": product_id},
            )
        except ApiError as error:
            flash(error.message, "error")
            return redirect(url_for("products"))

        return render_template(
            "product_detail.html",
            product=product,
            reviews=reviews_response.get("results", []),
        )

    @app.route("/products/<int:product_id>/add-to-cart", methods=["POST"])
    @login_required
    def add_to_cart(product_id: int):
        try:
            quantity = max(1, int(request.form.get("quantity", "1")))
        except ValueError:
            quantity = 1
        try:
            api_request(
                "POST",
                f"{DJANGO_API_URL}/api/shop/cart/add/",
                json={"product_id": product_id, "quantity": quantity},
                headers=auth_headers(),
            )
            flash("Товар добавлен в корзину", "success")
        except ApiError as error:
            flash(error.message, "error")
        return redirect(url_for("product_detail", product_id=product_id))

    @app.route("/products/<int:product_id>/reviews", methods=["POST"])
    @login_required
    def create_review(product_id: int):
        try:
            rating = int(request.form.get("rating", "5"))
        except ValueError:
            rating = 5

        activate_now = request.form.get("activate_now") == "on"

        try:
            review = api_request(
                "POST",
                f"{UGC_API_URL}/api/ugc/reviews/",
                json={
                    "product_id": product_id,
                    "text": request.form.get("text", ""),
                    "rating": rating,
                },
                headers=auth_headers(),
                expected_statuses=(201,),
            )
            if activate_now:
                api_request(
                    "PATCH",
                    f"{UGC_API_URL}/api/ugc/reviews/{review['id']}/status/",
                    json={"status": "active"},
                )
                flash("Отзыв создан и активирован", "success")
            else:
                flash("Отзыв создан и отправлен на модерацию", "success")
        except ApiError as error:
            flash(error.message, "error")

        return redirect(url_for("product_detail", product_id=product_id))
