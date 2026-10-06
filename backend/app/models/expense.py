from sqlalchemy import Column, String, Numeric, ForeignKey, Text, DateTime
from .base import Base, TimestampMixin, generate_uuid

class Expense(Base, TimestampMixin):
    __tablename__ = 'expenses'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    category = Column(String)
    description = Column(Text)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String)
    expense_date = Column(DateTime)
    employee_id = Column(String, ForeignKey('employees.id'), nullable=True)
    notes = Column(Text)
