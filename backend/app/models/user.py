from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin, generate_uuid

class UserRole(str, enum.Enum):
    OWNER = "Owner"
    ADMIN = "Admin"
    MANAGER = "Manager"
    STAFF = "Staff"

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    employee_id = Column(String, ForeignKey('employees.id'), nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String(50), default=UserRole.STAFF.value, nullable=False)
    is_active = Column(Boolean, default=True)
    
    business = relationship('Business', back_populates='users')
    employee = relationship('Employee', back_populates='user', uselist=False)
