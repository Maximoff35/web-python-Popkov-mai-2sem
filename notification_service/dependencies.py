from fastapi import Header, HTTPException, status
from notification_service.config import Config


async def verify_service_token(x_service_token: str = Header(...)):
    """
    Проверяет service-to-service токен.
    """
    if x_service_token != Config.SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid service token',
        )