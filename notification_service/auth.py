from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError

SECRET_KEY = 'dev-secret-key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def authenticate_user(username: str, password: str) -> bool:
    """
    Учебная проверка логина и пароля для демонстрации JWT в notification service.

    В реальном проекте пользователи авторизуются через Django Auth API,
    а внутренние вызовы notification service защищаются service-to-service token.
    """
    return username == 'admin' and password == 'admin'

def create_access_token(username: str) -> str:
    """
    Создаёт JWT access-токен.
    """
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': username,
        'exp': expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Проверяет Bearer-токен и возвращает имя пользователя.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    return username