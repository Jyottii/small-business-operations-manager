from sqlalchemy import Column, String, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class Supplier(Base, TimestampMixin):
    __tablename__ = 'suppliers'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    company_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    tax_identifier = Column(String)
    payment_terms = Column(String)
    outstanding_balance = Column(Numeric(12, 2), default=0.0)
    notes = Column(Text)
    
    business = relationship('Business', back_populates='suppliers')
    purchase_orders = relationship('PurchaseOrder', back_populates='supplier')
    payments = relationship('Payment', back_populates='supplier')
