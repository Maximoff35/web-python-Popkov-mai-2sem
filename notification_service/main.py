from fastapi import FastAPI
from notification_service.schemas import NotificationCreateSchema, NotificationResponseSchema


app = FastAPI(
    title='Notification Service',
    description='FastAPI-сервис для уведомлений.',
    version='1.0.0',
)

@app.get('/api/notifications/health/')
async def health_check():
    return {
        'status': 'ok',
        'service': 'notifications',
    }

@app.post(
    '/api/notifications/order-created/',
    response_model=NotificationResponseSchema,
    status_code=202,
)
async def create_order_notification(data: NotificationCreateSchema):
    return {
        'status': 'accepted',
        'detail': f'Notification for order {data.order_id} scheduled.',
    }