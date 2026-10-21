import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.sql import func

class SRSDeck(Base):
    __tablename__ = "srs_decks"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    document_id = Column(String(255), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    topic = Column(String(255), nullable=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    cards = relationship("SRSCard", back_populates="deck", cascade="all, delete-orphan")
    owner = relationship("User", backref="srs_decks")

class SRSCard(Base):
    __tablename__ = "srs_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("srs_decks.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    card_type = Column(String(50), nullable=False) # e.g. 'definition', 'formula'
    difficulty = Column(String(50), nullable=True, default='medium')
    status = Column(String(50), nullable=True, default='new')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    deck = relationship("SRSDeck", back_populates="cards")
    owner = relationship("User", backref="srs_cards")
    review_history = relationship("ReviewHistory", back_populates="card", uselist=False, cascade="all, delete-orphan")

class ReviewHistory(Base):
    __tablename__ = "srs_review_history"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("srs_cards.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    next_review_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    review_count = Column(Integer, default=0)
    
    # SM-2 Algorithm fields
    easiness_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0) # in days
    
    card = relationship("SRSCard", back_populates="review_history")
    owner = relationship("User", backref="srs_review_history")
