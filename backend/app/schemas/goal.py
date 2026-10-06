from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.base import BaseORMModel

class BusinessGoalBase(BaseModel):
    title: str
    metric: str  # TOTAL_REVENUE, ORDER_COUNT, CUSTOMER_COUNT, PROFIT
    target_value: float
    period: str = "MONTHLY"  # MONTHLY, QUARTERLY, YEARLY
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True

class BusinessGoalCreate(BusinessGoalBase):
    pass

class BusinessGoalUpdate(BaseModel):
    title: Optional[str] = None
    metric: Optional[str] = None
    target_value: Optional[float] = None
    period: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class BusinessGoalResponse(BusinessGoalBase, BaseORMModel):
    id: str
    business_id: str
    current_value: float = 0.0
    progress_percent: float = 0.0
    status: str = "IN_PROGRESS"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
