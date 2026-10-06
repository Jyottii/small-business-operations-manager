from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from .base import Base, TimestampMixin, generate_uuid

class Warehouse(Base, TimestampMixin):
    __tablename__ = 'warehouses'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    address = Column(String)
    branch_id = Column(String, ForeignKey('branches.id'), nullable=True, index=True)
    manager_id = Column(String, ForeignKey('employees.id'))
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        UniqueConstraint('business_id', 'code', name='uq_business_warehouse_code'),
    )
    
    business = relationship('Business', back_populates='warehouses')
    branch = relationship('Branch', back_populates='warehouses')
    inventories = relationship('Inventory', back_populates='warehouse')
    stock_movements = relationship('StockMovement', back_populates='warehouse')
    purchase_orders = relationship('PurchaseOrder', back_populates='warehouse')
