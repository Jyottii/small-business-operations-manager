from enum import Enum
from sqlalchemy import Column, String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from .base import Base, TimestampMixin, generate_uuid

class StockTransferStatus(str, Enum):
    DRAFT = "Draft"
    PENDING = "Pending"
    IN_TRANSIT = "In Transit"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class StockTransfer(Base, TimestampMixin):
    __tablename__ = 'stock_transfers'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    transfer_number = Column(String, nullable=False, index=True)
    source_warehouse_id = Column(String, ForeignKey('warehouses.id'), nullable=False, index=True)
    destination_warehouse_id = Column(String, ForeignKey('warehouses.id'), nullable=False, index=True)
    status = Column(String, default=StockTransferStatus.DRAFT.value) # Draft, Pending, In Transit, Completed, Cancelled
    requested_date = Column(DateTime)
    shipped_date = Column(DateTime)
    received_date = Column(DateTime)
    notes = Column(Text)
    created_by = Column(String, ForeignKey('users.id'), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('business_id', 'transfer_number', name='uq_business_transfer_number'),
    )
    
    business = relationship('Business')
    source_warehouse = relationship('Warehouse', foreign_keys=[source_warehouse_id])
    destination_warehouse = relationship('Warehouse', foreign_keys=[destination_warehouse_id])
    creator = relationship('User', foreign_keys=[created_by])
    items = relationship('StockTransferItem', back_populates='transfer', cascade='all, delete-orphan')

class StockTransferItem(Base, TimestampMixin):
    __tablename__ = 'stock_transfer_items'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    transfer_id = Column(String, ForeignKey('stock_transfers.id'), nullable=False, index=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Numeric(12, 2), nullable=False)
    
    transfer = relationship('StockTransfer', back_populates='items')
    product = relationship('Product')

    @property
    def stock_transfer_id(self):
        return self.transfer_id
