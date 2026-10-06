from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from .base import BaseORMModel

class SupplierBase(BaseModel):
    name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    tax_identifier: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    tax_identifier: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None

class SupplierResponse(SupplierBase, BaseORMModel):
    id: str
    business_id: str
    outstanding_balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
