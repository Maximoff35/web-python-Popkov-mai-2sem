import os


DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://127.0.0.1:8000")
UGC_API_URL = os.getenv("UGC_API_URL", "http://127.0.0.1:5000")
NOTIFICATION_API_URL = os.getenv("NOTIFICATION_API_URL", "http://127.0.0.1:8001")
FRONTEND_SECRET_KEY = os.getenv("FRONTEND_SECRET_KEY", "frontend-secret")
REQUEST_TIMEOUT = float(os.getenv("FRONTEND_REQUEST_TIMEOUT", "5"))
