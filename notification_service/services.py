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
    """
    url = f'{Config.DJANGO_SHOP_API_URL}/orders/{order_id}/'
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(url)
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Django shop service unavailable',
        )
    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found',
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Unexpected response from Django shop service',
        )
    return response.json()