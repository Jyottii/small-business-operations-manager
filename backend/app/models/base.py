import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_mixin
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@declarative_mixin
class BusinessOwnedMixin:
    business_id = Column(String, index=True, nullable=False)
