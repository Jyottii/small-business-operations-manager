from sqlalchemy import Column, String, ForeignKey, Text, JSON
from .base import Base, TimestampMixin, generate_uuid

class AuditLog(Base, TimestampMixin):
    __tablename__ = 'audit_logs'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String, nullable=False)
    entity_type = Column(String)
    entity_id = Column(String)
    description = Column(Text)
    metadata_info = Column('metadata', JSON)
