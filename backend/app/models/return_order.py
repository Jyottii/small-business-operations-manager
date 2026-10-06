from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models.base import Base, TimestampMixin, BusinessOwnedMixin

class Return(Base, TimestampMixin, BusinessOwnedMixin):
    __tablename__ = 'returns'

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    order_id = Column(String(36), ForeignKey('orders.id'), nullable=False)
    return_number = Column(String(50), nullable=False)
    status = Column(String(50), default='Pending') # Pending, Processed, Rejected
    refund_amount = Column(Numeric(12, 2), default=0.0)
    return_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(1000))

    order = relationship('Order', backref='returns')
    return_items = relationship('ReturnItem', back_populates='return_order')

class ReturnItem(Base, TimestampMixin):
    __tablename__ = 'return_items'

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    return_id = Column(String(36), ForeignKey('returns.id'), nullable=False)
    order_item_id = Column(String(36), ForeignKey('order_items.id'), nullable=False)
    product_id = Column(String(36), ForeignKey('products.id'), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)
    refund_amount = Column(Numeric(12, 2), default=0.0)
    reason = Column(String(255))

    return_order = relationship('Return', back_populates='return_items')
    product = relationship('Product')
    order_item = relationship('OrderItem')
