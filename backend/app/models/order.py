from sqlalchemy import Column, String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from .base import Base, TimestampMixin, generate_uuid

class Order(Base, TimestampMixin):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    customer_id = Column(String, ForeignKey('customers.id'), index=True)
    employee_id = Column(String, ForeignKey('employees.id'), index=True)
    branch_id = Column(String, ForeignKey('branches.id'), nullable=True, index=True)
    order_number = Column(String, nullable=False)
    status = Column(String, default='Pending')
    subtotal = Column(Numeric(12, 2), default=0.0)
    discount = Column(Numeric(12, 2), default=0.0)
    tax = Column(Numeric(12, 2), default=0.0)
    total = Column(Numeric(12, 2), default=0.0)
    amount_paid = Column(Numeric(12, 2), default=0.0)
    balance_due = Column(Numeric(12, 2), default=0.0)
    payment_status = Column(String, default='Unpaid')
    order_date = Column(DateTime)
    notes = Column(Text)
    
    __table_args__ = (
        UniqueConstraint('business_id', 'order_number', name='uq_business_order_number'),
    )
    
    customer = relationship('Customer', back_populates='orders')
    employee = relationship('Employee', back_populates='orders')
    branch = relationship('Branch', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')
    payments = relationship('Payment', back_populates='order')

    @property
    def total_amount(self):
        return self.total

    @total_amount.setter
    def total_amount(self, value):
        self.total = value
