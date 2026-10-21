import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy import JSON, Uuid as UUID
from app.db.base import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Optional metadata depending on document type
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    
    # The extracted text
    text_content = Column(Text, nullable=False)
    
    # Any additional metadata specific to the chunk (e.g., font sizes, slide notes)
    extracted_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
