from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class TutorSession(Base):
    __tablename__ = "tutor_sessions"

    id = Column(String(255), primary_key=True, default=generate_uuid, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    document_id = Column(String(255), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="tutor_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("tutor_sessions.id"), nullable=False)
    role = Column(String(255), nullable=False)  # 'user' or 'ai'
    content = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=True) # Stores the StructuredAnswer for AI messages
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("TutorSession", back_populates="messages")
