from flask import Flask

from frontend.routes.auth import register_auth_routes
from frontend.routes.cart import register_cart_routes
from frontend.routes.layout import register_layout_helpers
from frontend.routes.orders import register_order_routes
from frontend.routes.products import register_product_routes


def register_routes(app: Flask) -> None:
    register_layout_helpers(app)
    register_auth_routes(app)
    register_product_routes(app)
    register_cart_routes(app)
    register_order_routes(app)
