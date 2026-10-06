from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class PurchaseOrderItemCreate(BaseModel):
    product_id: str
    quantity_ordered: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(..., ge=0)

class PurchaseOrderCreate(BaseModel):
    supplier_id: str
    warehouse_id: str
    expected_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderReceive(BaseModel):
    items: dict[str, Decimal] # product_id -> quantity to receive (must be > 0 and <= outstanding)
    notes: Optional[str] = None

class PurchaseOrderItemResponse(BaseORMModel):
    id: str
    product_id: str
    quantity_ordered: Decimal
    quantity_received: Decimal
    unit_cost: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    line_total: Decimal

class PurchaseOrderResponse(BaseORMModel):
    id: str
    business_id: str
    supplier_id: str
    warehouse_id: str
    purchase_order_number: str
    status: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    expected_date: Optional[datetime] = None
    order_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    purchase_items: List[PurchaseOrderItemResponse] = []
