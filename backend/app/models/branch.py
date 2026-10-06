from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from .base import Base, TimestampMixin, generate_uuid

class Branch(Base, TimestampMixin):
    __tablename__ = 'branches'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    phone = Column(String)
    email = Column(String)
    manager_id = Column(String, ForeignKey('employees.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        UniqueConstraint('business_id', 'code', name='uq_business_branch_code'),
    )
    
    business = relationship('Business', back_populates='branches')
    manager = relationship('Employee', foreign_keys=[manager_id])
    warehouses = relationship('Warehouse', back_populates='branch')
    orders = relationship('Order', back_populates='branch')
