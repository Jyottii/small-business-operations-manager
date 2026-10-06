from sqlalchemy import Column, String, ForeignKey, Integer
from .base import Base, TimestampMixin, generate_uuid

class Document(Base, TimestampMixin):
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True, default=generate_uuid)
    business_id = Column(String, ForeignKey('businesses.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    document_type = Column(String)
    file_name = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    related_entity_type = Column(String)
    related_entity_id = Column(String)
    uploaded_by = Column(String, ForeignKey('users.id'))
