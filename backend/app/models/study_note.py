import uuid
from datetime import datetime
from sqlalchemy import Integer, Column, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy import Uuid as UUID
from app.db.base import Base

class StudyNote(Base):
    """
    Stores AI-generated study materials (notes, cheat sheets, interview prep)
    associated with a specific document and user.
    """
    __tablename__ = "study_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    note_type = Column(String(50), nullable=False) # 'short', 'detailed', 'revision', 'exam', 'interview', 'cheat_sheet'
    content = Column(Text, nullable=False) # The markdown content
    
    created_at = Column(DateTime, default=datetime.utcnow)
