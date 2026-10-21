import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Uuid as UUID
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False) # Size in bytes
    content_type = Column(String(255), nullable=False)
    
    upload_status = Column(String(255), default="uploaded") # Can be 'uploaded', 'processing', 'completed', 'failed'
    embedding_status = Column(String(255), default="unprocessed") # 'unprocessed', 'processing', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to PDFMetadata
    metadata_info = relationship("PDFMetadata", back_populates="document", uselist=False, cascade="all, delete-orphan")

class PDFMetadata(Base):
    __tablename__ = "pdf_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    author = Column(String(255), nullable=True)
    creation_date = Column(DateTime, nullable=True)
    page_count = Column(Integer, default=0)
    
    document = relationship("Document", back_populates="metadata_info")
