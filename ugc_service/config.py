import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'UGC_DATABASE_URL',
        'sqlite:///ugc.sqlite3'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DJANGO_SHOP_API_URL = os.getenv(
        'DJANGO_SHOP_API_URL',
        'http://127.0.0.1:8000/api/shop'
    )

    DJANGO_AUTH_ME_URL = os.getenv(
        'DJANGO_AUTH_ME_URL',
        'http://127.0.0.1:8000/api/auth/me/'
    )
    