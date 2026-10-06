from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class ProductBase(BaseModel):
    category_id: Optional[str] = None
    sku: str
    barcode: Optional[str] = None
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    tax_rate: Optional[Decimal] = Field(None, ge=0)
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, ge=0)
    expiry_tracking_enabled: bool = False
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    category_id: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    tax_rate: Optional[Decimal] = Field(None, ge=0)
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, ge=0)
    expiry_tracking_enabled: Optional[bool] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase, BaseORMModel):
    id: str
    business_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
