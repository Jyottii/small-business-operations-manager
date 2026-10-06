from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class PaymentCreate(BaseModel):
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    order_id: Optional[str] = None
    purchase_order_id: Optional[str] = None
    payment_method: str
    amount: Decimal = Field(..., gt=0)
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentResponse(BaseORMModel):
    id: str
    business_id: str
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    order_id: Optional[str] = None
    purchase_order_id: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    payment_method: Optional[str] = None
    amount: Decimal
    transaction_reference: Optional[str] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
