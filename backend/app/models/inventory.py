from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from .base import Base, TimestampMixin, generate_uuid

class Inventory(Base, TimestampMixin):
    __tablename__ = 'inventories'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    product_id = Column(String, ForeignKey('products.id'), nullable=False, index=True)
    warehouse_id = Column(String, ForeignKey('warehouses.id'), nullable=False, index=True)
    quantity = Column(Numeric(12, 2), default=0.0)
    reserved_quantity = Column(Numeric(12, 2), default=0.0)
    reorder_level = Column(Numeric(12, 2), default=0.0)
    reorder_quantity = Column(Numeric(12, 2), default=0.0)
    last_stock_update = Column(DateTime)
    
    __table_args__ = (
        UniqueConstraint('product_id', 'warehouse_id', name='uq_product_warehouse'),
    )
    
    product = relationship('Product', back_populates='inventories')
    warehouse = relationship('Warehouse', back_populates='inventories')
