from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from notification_service.schemas import (
    NotificationCreateSchema,
    NotificationResponseSchema,
    TokenResponseSchema,
    TokenRequestSchema,
)
from notification_service.services import send_order_created_notification, get_order_from_django
from notification_service.auth import (
    create_access_token,
    authenticate_user,
    get_current_user,
)

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
    '/api/notifications/auth/token',
    response_model=TokenResponseSchema,
)
async def login(data: TokenRequestSchema):
    if not authenticate_user(data.username, data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
        )
    access_token = create_access_token(data.username)
    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }

@app.get('/api/notifications/check-order/{order_id}/')
async def check_order(order_id: int):
    order = await get_order_from_django(order_id)
    return {
        'status': 'ok',
        'order': order,
    }

@app.get('/api/notifications/protected/')
async def protected_endpoint(current_user: str = Depends(get_current_user)):
    return {
        'message': 'Доступ разрешен.',
        'user': current_user,
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