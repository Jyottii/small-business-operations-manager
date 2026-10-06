import os

dirs = ['app/schemas', 'app/services', 'app/routers', 'app/dependencies', 'app/core']
for d in dirs:
    os.makedirs(d, exist_ok=True)

with open('app/core/exceptions.py', 'w') as f:
    f.write('''from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ConflictException(HTTPException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
''')

with open('app/dependencies/database.py', 'w') as f:
    f.write('''from typing import Generator
from app.core.database import SessionLocal

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
''')

with open('app/dependencies/auth.py', 'w') as f:
    f.write('''from fastapi import Header, Depends
from app.core.exceptions import BadRequestException

def get_current_business_id(x_business_id: str = Header(..., description="Temporary dev header for multi-tenant context")) -> str:
    if not x_business_id:
        raise BadRequestException("X-Business-ID header is required")
    return x_business_id
''')

with open('app/schemas/base.py', 'w') as f:
    f.write('''from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

T = TypeVar('T')

class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int

class ResponseModel(BaseModel, Generic[T]):
    data: T

class PaginatedResponseModel(BaseModel, Generic[T]):
    data: List[T]
    pagination: PaginationInfo

class BaseORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
''')
