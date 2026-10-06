from sqlalchemy import Column, String, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class StockMovement(Base, TimestampMixin):
    __tablename__ = 'stock_movements'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False, index=True)
    warehouse_id = Column(String, ForeignKey('warehouses.id'), nullable=False, index=True)
    movement_type = Column(String, nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)
    reference_type = Column(String)
    reference_id = Column(String)
    previous_quantity = Column(Numeric(12, 2))
    resulting_quantity = Column(Numeric(12, 2))
    unit_cost = Column(Numeric(12, 2))
    notes = Column(Text)
    
    product = relationship('Product', back_populates='stock_movements')
    warehouse = relationship('Warehouse', back_populates='stock_movements')
