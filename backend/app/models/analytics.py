from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy import UUID
import uuid

class Analytics(Base):
    __tablename__ = "analytics_profile"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_study_hours = Column(Float, default=0.0)
    last_active_date = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", backref="analytics_profile")

class StudySession(Base):
    __tablename__ = "analytics_study_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    duration_minutes = Column(Integer, default=0)
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="study_sessions")

class QuizResult(Base):
    __tablename__ = "analytics_quiz_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    accuracy_percentage = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="quiz_results")

class Performance(Base):
    __tablename__ = "analytics_performance"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    strong_score = Column(Float, default=0.0)
    weak_score = Column(Float, default=0.0)
    
    user = relationship("User", backref="performance")
