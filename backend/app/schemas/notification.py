from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .base import BaseORMModel

class NotificationResponse(BaseORMModel):
    id: str
    business_id: str
    user_id: Optional[str] = None
    title: str
    message: str
    notification_type: str
    is_read: bool
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    created_at: datetime
