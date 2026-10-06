from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class ReturnItemCreate(BaseModel):
    product_id: str
    quantity: Decimal = Field(..., gt=0)
    reason: Optional[str] = "Customer Return"

class ReturnCreate(BaseModel):
    items: List[ReturnItemCreate]
    notes: Optional[str] = None

class ReturnItemResponse(BaseORMModel):
    id: str
    return_id: str
    order_item_id: str
    product_id: str
    quantity: Decimal
    refund_amount: Decimal
    reason: Optional[str] = None
    created_at: datetime

class ReturnResponse(BaseORMModel):
    id: str
    business_id: str
    order_id: str
    return_number: str
    status: str
    refund_amount: Decimal
    return_date: datetime
    notes: Optional[str] = None
    created_at: datetime
    return_items: List[ReturnItemResponse] = []
