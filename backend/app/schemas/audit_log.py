from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel
from .base import BaseORMModel

class AuditLogResponse(BaseORMModel):
    id: str
    business_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    description: Optional[str] = None
    metadata_info: Optional[Any] = None
    created_at: Optional[datetime] = None
