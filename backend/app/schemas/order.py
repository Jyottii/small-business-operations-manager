from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: Decimal = Field(..., gt=0)
    discount: Decimal = Field(default=Decimal('0.0'), ge=Decimal('0.0'))

class OrderCreate(BaseModel):
    warehouse_id: Optional[str] = None
    customer_id: Optional[str] = None
    employee_id: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderItemResponse(BaseORMModel):
    id: str
    product_id: str
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    line_total: Decimal

class OrderResponse(BaseORMModel):
    id: str
    business_id: str
    customer_id: Optional[str] = None
    employee_id: Optional[str] = None
    order_number: str
    status: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    payment_status: str
    order_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_items: List[OrderItemResponse] = []
