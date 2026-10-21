from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.models.srs_flashcard import SRSDeck, SRSCard, ReviewHistory
from app.DTOs.srs_flashcard import SRSDeckCreate, SRSCardCreate

class SRSFlashcardService:
    def __init__(self, db: Session):
        self.db = db

    def get_decks(self, user_id: int):
        decks = self.db.query(SRSDeck).filter(SRSDeck.owner_id == user_id).all()
        now = datetime.utcnow()
        
        # Calculate due cards for each deck
        for deck in decks:
            deck.total_cards = len(deck.cards)
            due = 0
            for card in deck.cards:
                if card.review_history and card.review_history.next_review_date:
                    nrd = card.review_history.next_review_date
                    if nrd.tzinfo:
                        nrd = nrd.replace(tzinfo=None)
                    if nrd <= now:
                        due += 1
            deck.due_cards = due
        return decks

    def create_deck(self, user_id: int, deck_in: SRSDeckCreate):
        deck = SRSDeck(
            owner_id=user_id, 
            title=deck_in.title, 
            description=deck_in.description,
            topic=deck_in.topic,
            document_id=deck_in.document_id
        )
        self.db.add(deck)
        self.db.flush() # get deck.id
        
        for card_in in deck_in.cards:
            card = self.add_card(user_id, deck.id, card_in, commit=False)
            self.db.flush() # get card.id
            rh = ReviewHistory(card_id=card.id, owner_id=user_id)
            self.db.add(rh)
            
        try:
            self.db.commit()
            self.db.refresh(deck)
            return deck
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to save deck to database.")

    def delete_deck(self, user_id: int, deck_id: int):
        deck = self.db.query(SRSDeck).filter(SRSDeck.owner_id == user_id, SRSDeck.id == deck_id).first()
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        self.db.delete(deck)
        self.db.commit()

    def update_deck(self, user_id: int, deck_id: int, deck_in):
        deck = self.db.query(SRSDeck).filter(SRSDeck.owner_id == user_id, SRSDeck.id == deck_id).first()
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        update_data = deck_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(deck, field, value)
            
        self.db.commit()
        self.db.refresh(deck)
        return deck

    def add_card(self, user_id: int, deck_id: int, card_in: SRSCardCreate, commit=True):
        card = SRSCard(
            owner_id=user_id,
            deck_id=deck_id,
            question=card_in.question,
            answer=card_in.answer,
            card_type=card_in.card_type,
            difficulty=card_in.difficulty
        )
        self.db.add(card)
        self.db.flush()
        
        # Initialize review history for new card
        history = ReviewHistory(card_id=card.id, owner_id=user_id, next_review_date=datetime.utcnow())
        self.db.add(history)
        
        if commit:
            self.db.commit()
            self.db.refresh(card)
        return card

    def delete_card(self, user_id: int, card_id: int):
        card = self.db.query(SRSCard).filter(SRSCard.owner_id == user_id, SRSCard.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        self.db.delete(card)
        self.db.commit()

    def get_due_cards(self, user_id: int, deck_id: int):
        now = datetime.utcnow()
        cards = self.db.query(SRSCard).join(ReviewHistory).filter(
            SRSCard.owner_id == user_id,
            SRSCard.deck_id == deck_id,
            ReviewHistory.next_review_date <= now
        ).all()
        return cards

    def save_score(self, user_id: int, card_id: int, quality: int):
        """
        Implements SuperMemo-2 (SM-2) Spaced Repetition Algorithm.
        Quality: 0-5
        0: Complete blackout
        1: Incorrect response
        2: Incorrect response; where the correct one seemed easy to recall
        3: Correct response recalled with serious difficulty
        4: Correct response after a hesitation
        5: Perfect response
        """
        history = self.db.query(ReviewHistory).filter(
            ReviewHistory.owner_id == user_id,
            ReviewHistory.card_id == card_id
        ).first()
        
        if not history:
            raise HTTPException(status_code=404, detail="Review history not found")

        # Update correct/wrong counters
        if quality >= 3:
            history.correct_answers += 1
        else:
            history.wrong_answers += 1
            
        history.review_count += 1
        history.last_reviewed = datetime.utcnow()

        # SM-2 Logic
        if quality < 3:
            # Failed to recall
            history.interval = 1
        else:
            # Recalled correctly
            if history.review_count == 1:
                history.interval = 1
            elif history.review_count == 2:
                history.interval = 6
            else:
                history.interval = int(history.interval * history.easiness_factor)

        # Update Easiness Factor (EF)
        # EF := EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        history.easiness_factor = history.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        if history.easiness_factor < 1.3:
            history.easiness_factor = 1.3
            
        # Calculate next review date
        history.next_review_date = datetime.utcnow() + timedelta(days=history.interval)
        
        self.db.commit()
        return {"status": "success", "next_review_date": history.next_review_date, "interval": history.interval}
