from sqlalchemy import Column, String, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class Customer(Base, TimestampMixin):
    __tablename__ = 'customers'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    customer_type = Column(String)
    credit_limit = Column(Numeric(12, 2), default=0.0)
    outstanding_balance = Column(Numeric(12, 2), default=0.0)
    notes = Column(Text)
    
    business = relationship('Business', back_populates='customers')
    orders = relationship('Order', back_populates='customer')
    payments = relationship('Payment', back_populates='customer')
