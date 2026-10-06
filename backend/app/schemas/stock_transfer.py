from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.base import BaseORMModel

class StockTransferItemBase(BaseModel):
    product_id: str
    quantity: float

class StockTransferItemCreate(StockTransferItemBase):
    pass

class StockTransferItemResponse(StockTransferItemBase, BaseORMModel):
    id: str
    transfer_id: str
    product_name: Optional[str] = None
    product_sku: Optional[str] = None

class StockTransferBase(BaseModel):
    source_warehouse_id: str
    destination_warehouse_id: str
    notes: Optional[str] = None

class StockTransferCreate(StockTransferBase):
    items: List[StockTransferItemCreate]

class StockTransferStatusUpdate(BaseModel):
    status: str  # Pending, In Transit, Completed, Cancelled
    notes: Optional[str] = None

class StockTransferResponse(StockTransferBase, BaseORMModel):
    id: str
    business_id: str
    transfer_number: str
    status: str
    source_warehouse_name: Optional[str] = None
    destination_warehouse_name: Optional[str] = None
    created_by: Optional[str] = None
    requested_date: Optional[datetime] = None
    shipped_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[StockTransferItemResponse] = []
