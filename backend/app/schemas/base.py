from typing import Generic, TypeVar, List, Optional, Any
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
