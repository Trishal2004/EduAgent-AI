import uuid
from datetime import datetime
from sqlalchemy import Integer, Column, String, ForeignKey, DateTime
from sqlalchemy import JSON, Uuid as UUID
from app.db.base import Base

class QuestionPaper(Base):
    __tablename__ = "question_papers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    paper_type = Column(String(50), nullable=False) # e.g., "university_pattern"
    content_json = Column(JSON, nullable=False) # The structured sections (2 marks, 5 marks, 10 marks)
    pdf_file_path = Column(String(255), nullable=True) # Path to the generated PDF on disk
    
    created_at = Column(DateTime, default=datetime.utcnow)
