from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class Business(Base, TimestampMixin):
    __tablename__ = 'businesses'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    legal_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postal_code = Column(String)
    tax_identifier = Column(String)
    currency = Column(String, default='USD')
    timezone = Column(String, default='UTC')
    
    users = relationship('User', back_populates='business')
    employees = relationship('Employee', back_populates='business')
    customers = relationship('Customer', back_populates='business')
    suppliers = relationship('Supplier', back_populates='business')
    products = relationship('Product', back_populates='business')
    categories = relationship('Category', back_populates='business')
    warehouses = relationship('Warehouse', back_populates='business')
    branches = relationship('Branch', back_populates='business')
