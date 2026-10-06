from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class Employee(Base, TimestampMixin):
    __tablename__ = 'employees'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    designation = Column(String)
    department = Column(String)
    joining_date = Column(String)
    salary = Column(Numeric(12, 2))
    status = Column(String, default='Active')
    
    business = relationship('Business', back_populates='employees')
    user = relationship('User', back_populates='employee')
    orders = relationship('Order', back_populates='employee')
