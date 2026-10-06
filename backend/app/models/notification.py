from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from .base import Base, TimestampMixin, generate_uuid

class Notification(Base, TimestampMixin):
    __tablename__ = 'notifications'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text)
    notification_type = Column(String)
    is_read = Column(Boolean, default=False)
    related_entity_type = Column(String)
    related_entity_id = Column(String)
