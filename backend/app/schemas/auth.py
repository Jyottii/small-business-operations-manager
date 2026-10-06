from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .user import UserResponse

class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    business_name: Optional[str] = Field(None, max_length=100)
    business_id: Optional[str] = None
    role: Optional[str] = Field(None, description="Owner, Admin, Manager, or Staff")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
