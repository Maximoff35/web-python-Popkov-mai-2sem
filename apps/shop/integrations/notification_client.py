import logging
import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def notify_order_created(order_id: int, user_id: int) -> None:
    """
    Уведомляет FastAPI notification service о создании заказа.
    Ошибка уведомления не должна ломать создание заказа.
    """
    url = f'{settings.NOTIFICATION_SERVICE_URL}/order-created/'
    payload = {
        'order_id': order_id,
        'user_id': user_id,
        'message': f'Order {order_id} created.',
    }
    try:
        response = requests.post(url, json=payload, timeout=3)
        response.raise_for_status()
    except requests.RequestException as error:
        logger.warning('Failed to notify notification service about order %s: %s', order_id, error)