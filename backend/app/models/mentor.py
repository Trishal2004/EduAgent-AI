import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Float, JSON, Uuid as UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class MentorStudyPlan(Base):
    __tablename__ = "mentor_study_plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_type = Column(String(50), nullable=False) # 'daily', 'weekly'
    content = Column(JSON, nullable=False) # e.g. list of tasks
    created_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    action_type = Column(String(100), nullable=False) # 'review', 'quiz', 'read'
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class WeakTopic(Base):
    __tablename__ = "weak_topics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_name = Column(String(255), nullable=False)
    score_indicator = Column(Float, nullable=True) # e.g. 45.0 for 45%
    identified_at = Column(DateTime, default=datetime.utcnow)

class Goal(Base):
    __tablename__ = "goals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_text = Column(String(255), nullable=False)
    target_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="active") # active, completed
    created_at = Column(DateTime, default=datetime.utcnow)

class MentorChat(Base):
    __tablename__ = "mentor_chats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False) # 'user' or 'ai'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
