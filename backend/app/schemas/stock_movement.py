from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from .base import BaseORMModel

class StockMovementResponse(BaseORMModel):
    id: str
    business_id: str
    product_id: str
    warehouse_id: str
    movement_type: str
    quantity: Decimal
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    previous_quantity: Optional[Decimal] = None
    resulting_quantity: Optional[Decimal] = None
    unit_cost: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime
