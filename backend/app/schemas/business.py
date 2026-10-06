from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .base import BaseORMModel

class BusinessBase(BaseModel):
    name: str
    legal_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    tax_identifier: Optional[str] = None
    currency: str = "USD"
    timezone: str = "UTC"

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    tax_identifier: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None

class BusinessResponse(BusinessBase, BaseORMModel):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
