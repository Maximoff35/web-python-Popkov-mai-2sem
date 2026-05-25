import logging
import time
import httpx
from fastapi import HTTPException, status
from notification_service.config import Config


logger = logging.getLogger(__name__)


def send_order_created_notification(order_id: int, user_id: int, message: str) -> None:
    """
    Имитирует отправку уведомления при создании заказа.
    Фоновая задача.
    """
    logger.info(
        'Sending order notification: order_id=%s, user_id=%s, message=%s',
        order_id,
        user_id,
        message,
    )
    time.sleep(1)
    logger.info('Order notification sent: order_id=%s, user_id=%s', order_id, user_id)

async def get_order_from_django(order_id: int) -> dict:
    """
    Асинхронно получает данные заказа из Django API.

    Endpoint используется как учебная демонстрация async HTTP-интеграции.
    Основной production-сценарий интеграции: Django сам отправляет событие
    о создании заказа в notification service через service-to-service token.
    """
    url = f'{Config.DJANGO_SHOP_API_URL}/orders/{order_id}/'
    logger.info(
        'Requesting order from Django API: order_id=%s',
        order_id,
    )
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(url)
    except httpx.RequestError:
        logger.error(
            'Django shop service unavailable while requesting order: order_id=%s',
            order_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Django shop service unavailable',
        )
    if response.status_code == 404:
        logger.warning(
            'Order not found in Django API: order_id=%s',
            order_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found',
        )
    if response.status_code != 200:
        logger.error(
            'Unexpected Django API response: order_id=%s status_code=%s',
            order_id,
            response.status_code,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Unexpected response from Django shop service',
        )
    logger.info(
        'Order received from Django API: order_id=%s',
        order_id,
    )
    return response.json()