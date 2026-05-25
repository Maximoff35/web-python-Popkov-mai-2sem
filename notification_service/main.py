from fastapi import FastAPI, BackgroundTasks
from notification_service.schemas import NotificationCreateSchema, NotificationResponseSchema
from notification_service.services import send_order_created_notification


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
async def create_order_notification(data: NotificationCreateSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        send_order_created_notification,
        order_id=data.order_id,
        user_id=data.user_id,
        message=data.message,
    )
    return {
        'status': 'accepted',
        'detail': f'Notification for order {data.order_id} scheduled.',
    }