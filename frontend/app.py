from flask import Flask

from frontend.routes import register_routes
from frontend.settings import FRONTEND_SECRET_KEY

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = FRONTEND_SECRET_KEY
    register_routes(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5050)
