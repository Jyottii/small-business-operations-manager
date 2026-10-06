from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class PurchaseOrderItem(Base, TimestampMixin):
    __tablename__ = 'purchase_order_items'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    purchase_order_id = Column(String, ForeignKey('purchase_orders.id'), nullable=False, index=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False, index=True)
    quantity_ordered = Column(Numeric(12, 2), nullable=False)
    quantity_received = Column(Numeric(12, 2), default=0.0)
    unit_cost = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=0.0)
    tax_amount = Column(Numeric(12, 2), default=0.0)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    purchase_order = relationship('PurchaseOrder', back_populates='purchase_items')
    product = relationship('Product', back_populates='purchase_order_items')
