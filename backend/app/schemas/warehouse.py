from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .base import BaseORMModel

class WarehouseBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    manager_id: Optional[str] = None
    branch_id: Optional[str] = None
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    manager_id: Optional[str] = None
    branch_id: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase, BaseORMModel):
    id: str
    business_id: str
    branch_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class WarehouseSummaryResponse(BaseModel):
    warehouse: WarehouseResponse
    total_products: int
    total_stock: int
    total_valuation: float
    low_stock_count: int
    out_of_stock_count: int
