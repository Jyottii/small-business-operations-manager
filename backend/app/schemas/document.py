from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.base import BaseORMModel

class DocumentResponse(BaseORMModel):
    id: str
    business_id: str
    name: str
    document_type: Optional[str] = None
    file_name: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: Optional[datetime] = None
