from sqlalchemy import Column, String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from .base import Base, TimestampMixin, generate_uuid

class PurchaseOrder(Base, TimestampMixin):
    __tablename__ = 'purchase_orders'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    supplier_id = Column(String, ForeignKey('suppliers.id'), nullable=False, index=True)
    warehouse_id = Column(String, ForeignKey('warehouses.id'), nullable=False, index=True)
    purchase_order_number = Column(String, nullable=False)
    status = Column(String, default='Draft')
    subtotal = Column(Numeric(12, 2), default=0.0)
    discount = Column(Numeric(12, 2), default=0.0)
    tax = Column(Numeric(12, 2), default=0.0)
    total = Column(Numeric(12, 2), default=0.0)
    amount_paid = Column(Numeric(12, 2), default=0.0)
    balance_due = Column(Numeric(12, 2), default=0.0)
    expected_date = Column(DateTime)
    order_date = Column(DateTime)
    notes = Column(Text)
    
    __table_args__ = (
        UniqueConstraint('business_id', 'purchase_order_number', name='uq_business_po_number'),
    )
    
    supplier = relationship('Supplier', back_populates='purchase_orders')
    warehouse = relationship('Warehouse', back_populates='purchase_orders')
    purchase_items = relationship('PurchaseOrderItem', back_populates='purchase_order')
    payments = relationship('Payment', back_populates='purchase_order')

    @property
    def po_number(self):
        return self.purchase_order_number

    @property
    def total_amount(self):
        return self.total

    @property
    def expected_delivery_date(self):
        return self.expected_date
