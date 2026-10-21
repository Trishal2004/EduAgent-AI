from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from app.models.flashcard import FlashcardDeck, Flashcard
from app.DTOs.flashcard import GeneratedFlashcard

class FlashcardRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_deck(self, document_id: Optional[UUID], owner_id: int, generated_cards: List[GeneratedFlashcard], topic: Optional[str] = None) -> FlashcardDeck:
        """Creates a deck and saves all associated cards in a single transaction."""
        # 1. Create Deck
        db_deck = FlashcardDeck(
            document_id=document_id,
            owner_id=owner_id,
            topic=topic
        )
        self.session.add(db_deck)
        self.session.flush() # Flush to get the deck.id
        
        # 2. Create Cards
        db_cards = [
            Flashcard(
                deck_id=db_deck.id,
                card_type=card.card_type.value,
                front=card.front,
                back=card.back
            ) for card in generated_cards
        ]
        
        self.session.add_all(db_cards)
        self.session.commit()
        
        # Reload deck with its relationships populated
        return self.get_deck_by_id(db_deck.id, owner_id)

    def get_decks_by_document(self, document_id: UUID, owner_id: int) -> List[FlashcardDeck]:
        result = self.session.execute(
            select(FlashcardDeck)
            .where(FlashcardDeck.document_id == document_id, FlashcardDeck.owner_id == owner_id)
            .order_by(FlashcardDeck.created_at.desc())
        )
        return result.scalars().all()
        
    def get_deck_by_id(self, deck_id: UUID, owner_id: int) -> Optional[FlashcardDeck]:
        result = self.session.execute(
            select(FlashcardDeck)
            .where(FlashcardDeck.id == deck_id, FlashcardDeck.owner_id == owner_id)
            .options(selectinload(FlashcardDeck.cards))
        )
        return result.scalars().first()
