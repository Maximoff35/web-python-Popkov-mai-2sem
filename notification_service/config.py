import os


class Config:
    DJANGO_SHOP_API_URL = os.getenv(
        'DJANGO_SHOP_API_URL',
        'http://127.0.0.1:8000/api/shop',
    )