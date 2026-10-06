from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class BusinessGoal(Base, TimestampMixin):
    __tablename__ = 'business_goals'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    title = Column(String, nullable=False)
    metric = Column(String, nullable=False) # sales_revenue, gross_profit, net_profit, new_customers, order_count
    target_value = Column(Numeric(12, 2), nullable=False)
    period = Column(String, default='current_month') # current_month, current_quarter, annual, custom
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    business = relationship('Business')
