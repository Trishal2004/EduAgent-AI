import uuid
from datetime import datetime
from sqlalchemy import Integer, Column, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy import Uuid as UUID
from app.db.base import Base

class FlashcardDeck(Base):
    """
    Represents a collection of flashcards generated from a document.
    """
    __tablename__ = "flashcard_decks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to cards
    cards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")

class Flashcard(Base):
    """
    Represents an individual flashcard.
    """
    __tablename__ = "flashcards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    deck_id = Column(UUID(as_uuid=True), ForeignKey("flashcard_decks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    card_type = Column(String(50), nullable=False) # definition, example, formula, interview, true_false
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    
    deck = relationship("FlashcardDeck", back_populates="cards")
