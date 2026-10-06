from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from .base import BaseORMModel

class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    customer_type: Optional[str] = None
    credit_limit: Decimal = Decimal('0.0')
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    customer_type: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    notes: Optional[str] = None

class CustomerResponse(CustomerBase, BaseORMModel):
    id: str
    business_id: str
    outstanding_balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
