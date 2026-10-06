from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from .base import Base, TimestampMixin, generate_uuid

class Product(Base, TimestampMixin):
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    category_id = Column(String, ForeignKey('categories.id'), nullable=True)
    sku = Column(String, nullable=False, index=True)
    barcode = Column(String)
    name = Column(String, nullable=False)
    description = Column(Text)
    unit = Column(String)
    cost_price = Column(Numeric(12, 2))
    selling_price = Column(Numeric(12, 2))
    tax_rate = Column(Numeric(5, 2))
    reorder_level = Column(Numeric(12, 2), default=0)
    reorder_quantity = Column(Numeric(12, 2), default=0)
    expiry_tracking_enabled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        UniqueConstraint('business_id', 'sku', name='uq_business_sku'),
    )
    
    business = relationship('Business', back_populates='products')
    category = relationship('Category', back_populates='products')
    inventories = relationship('Inventory', back_populates='product')
    stock_movements = relationship('StockMovement', back_populates='product')
    order_items = relationship('OrderItem', back_populates='product')
    purchase_order_items = relationship('PurchaseOrderItem', back_populates='product')
