from sqlalchemy import Column, String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class Payment(Base, TimestampMixin):
    __tablename__ = 'payments'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    customer_id = Column(String, ForeignKey('customers.id'), nullable=True, index=True)
    supplier_id = Column(String, ForeignKey('suppliers.id'), nullable=True, index=True)
    order_id = Column(String, ForeignKey('orders.id'), nullable=True, index=True)
    purchase_order_id = Column(String, ForeignKey('purchase_orders.id'), nullable=True, index=True)
    reference_type = Column(String)
    reference_id = Column(String)
    payment_method = Column(String)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_reference = Column(String)
    payment_date = Column(DateTime)
    notes = Column(Text)
    
    customer = relationship('Customer', back_populates='payments')
    supplier = relationship('Supplier', back_populates='payments')
    order = relationship('Order', back_populates='payments')
    purchase_order = relationship('PurchaseOrder', back_populates='payments')
