from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class ExpenseCreate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = None
    expense_date: Optional[datetime] = None
    notes: Optional[str] = None

class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_method: Optional[str] = None
    expense_date: Optional[datetime] = None
    notes: Optional[str] = None

class ExpenseResponse(BaseORMModel):
    id: str
    business_id: str
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Decimal
    payment_method: Optional[str] = None
    expense_date: Optional[datetime] = None
    employee_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
