from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from .base import BaseORMModel

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "Staff"
    employee_id: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    employee_id: Optional[str] = None

class UserResponse(BaseORMModel):
    id: str
    business_id: str
    employee_id: Optional[str] = None
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
