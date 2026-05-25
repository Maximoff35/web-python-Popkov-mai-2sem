import logging
import time


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