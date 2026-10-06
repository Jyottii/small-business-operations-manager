from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class InventoryAdjust(BaseModel):
    product_id: str
    warehouse_id: str
    quantity_change: Decimal # Negative for deduction, Positive for addition
    movement_type: str
    notes: Optional[str] = None

class InventoryResponse(BaseORMModel):
    id: str
    product_id: str
    warehouse_id: str
    quantity: Decimal
    reserved_quantity: Decimal
    reorder_level: Decimal
    reorder_quantity: Decimal
    last_stock_update: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
