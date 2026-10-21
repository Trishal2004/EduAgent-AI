import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy import JSON, Uuid as UUID
from app.db.base import Base

class ProcessedChunk(Base):
    """
    Stores the granular, semantic chunks that are ready for vector embeddings.
    These are derived from the raw DocumentChunk pages/sections.
    """
    __tablename__ = "processed_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Inherited metadata for context retention
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    
    # Ordering within the document
    chunk_index = Column(Integer, nullable=False)
    
    # The overlapping chunk text
    text_content = Column(Text, nullable=False)
    
    # Vector embedding using pgvector. 1536 is for text-embedding-3-small
    embedding = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
