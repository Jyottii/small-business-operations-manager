from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class OrderItem(Base, TimestampMixin):
    __tablename__ = 'order_items'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    order_id = Column(String, ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0.0)
    tax_rate = Column(Numeric(5, 2), default=0.0)
    tax_amount = Column(Numeric(12, 2), default=0.0)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')
