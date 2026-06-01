from flask import Flask, flash, redirect, render_template, request, session, url_for

from frontend.api import ApiError, api_request
from frontend.auth import auth_headers
from frontend.settings import DJANGO_API_URL


def register_auth_routes(app: Flask) -> None:
    @app.route("/register", methods=["GET", "POST"])
    def register():
        form_data = {
            "username": request.form.get("username", ""),
            "email": request.form.get("email", ""),
        }
        if request.method == "POST":
            try:
                api_request(
                    "POST",
                    f"{DJANGO_API_URL}/api/auth/register/",
                    json={
                        "username": request.form.get("username", "").strip(),
                        "email": request.form.get("email", "").strip(),
                        "password": request.form.get("password", ""),
                        "password_confirm": request.form.get("password_confirm", ""),
                    },
                    expected_statuses=(201,),
                )
            except ApiError as error:
                flash(error.message, "error")
            else:
                flash("Пользователь зарегистрирован", "success")
                return redirect(url_for("login"))
        return render_template("register.html", form_data=form_data)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form_data = {"username": request.form.get("username", "")}
        if request.method == "POST":
            try:
                tokens = api_request(
                    "POST",
                    f"{DJANGO_API_URL}/api/auth/login/",
                    json={
                        "username": request.form.get("username", "").strip(),
                        "password": request.form.get("password", ""),
                    },
                )
                session["access_token"] = tokens["access"]
                session["refresh_token"] = tokens.get("refresh")
                session["current_user"] = api_request(
                    "GET",
                    f"{DJANGO_API_URL}/api/auth/me/",
                    headers=auth_headers(),
                )
            except ApiError as error:
                session.clear()
                flash(error.message, "error")
            else:
                flash("Вход выполнен", "success")
                return redirect(url_for("products"))
        return render_template("login.html", form_data=form_data)

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        flash("Выход из системы", "success")
        return redirect(url_for("login"))
