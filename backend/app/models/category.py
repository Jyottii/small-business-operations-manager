from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, generate_uuid

class Category(Base, TimestampMixin):
    __tablename__ = 'categories'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    parent_category_id = Column(String, ForeignKey('categories.id'), nullable=True)
    
    business = relationship('Business', back_populates='categories')
    products = relationship('Product', back_populates='category')
