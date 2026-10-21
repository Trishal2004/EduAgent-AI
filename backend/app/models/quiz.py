import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy import JSON, Uuid as UUID, Boolean, Date
from app.db.base import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=True)
    difficulty = Column(String(50), nullable=False) # easy, medium, hard
    is_daily = Column(Boolean, default=False, index=True)
    quiz_date = Column(Date, nullable=True, index=True)
    quiz_number = Column(Integer, nullable=True)
    status = Column(String(50), default="Not Started") # Not Started, In Progress, Completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", foreign_keys=[document_id])
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

    @property
    def score(self):
        """Returns the score of the most recent attempt, if any."""
        return self.attempts[-1].score if self.attempts else None

    @property
    def question_count(self):
        """Returns the total number of questions."""
        return len(self.questions) if self.questions else 0

    @property
    def question_types(self):
        """Returns a list of unique question types."""
        return list(set(q.question_type for q in self.questions)) if self.questions else []

    @property
    def time_spent_seconds(self):
        return self.attempts[-1].time_spent_seconds if self.attempts else 0

    @property
    def document_filename(self):
        return self.document.filename if self.document else None

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    question_type = Column(String(50), nullable=False) # mcq, short, long, coding, case_study
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True) # Used for MCQs
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    
    quiz = relationship("Quiz", back_populates="questions")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    user_answers = Column(JSON, nullable=False) # Stores the submitted answers
    time_spent_seconds = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    quiz = relationship("Quiz", back_populates="attempts")
