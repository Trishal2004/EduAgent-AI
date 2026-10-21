import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Uuid as UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recent_files = relationship("RecentFile", back_populates="workspace", cascade="all, delete-orphan")
    pinned_documents = relationship("PinnedDocument", back_populates="workspace", cascade="all, delete-orphan")
    activities = relationship("RecentActivity", back_populates="workspace", cascade="all, delete-orphan")

class RecentFile(Base):
    __tablename__ = "recent_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    last_opened_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="recent_files")

class PinnedDocument(Base):
    __tablename__ = "pinned_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    pinned_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="pinned_documents")

class RecentActivity(Base):
    __tablename__ = "recent_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    activity_type = Column(String(50), nullable=False) # "upload", "quiz", "chat"
    description = Column(Text, nullable=False)
    reference_id = Column(String(255), nullable=True) # ID of the related object (e.g. document_id, tutor_session_id)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="activities")
