from pydantic import BaseModel, Field


class NotificationCreateSchema(BaseModel):
    """
    Схема входных данных для создания уведомления.
    """
    order_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    message: str = Field(..., min_length=1, max_length=500)

class NotificationResponseSchema(BaseModel):
    """
    Схема ответа после поступления уведомления в обработку.
    """
    status: str
    detail: str

