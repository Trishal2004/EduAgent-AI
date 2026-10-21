from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.security import deps
from app.models.user import User
from app.DTOs.flashcard import FlashcardDeckResponse, FlashcardDeckDetailResponse, FlashcardGenerateRequest
from app.services.flashcards_generation import FlashcardsGenerationService
from app.repositories.flashcard import FlashcardRepository

router = APIRouter()

@router.post("/flashcards/generate", response_model=FlashcardDeckDetailResponse)
async def generate_flashcards_from_topic(
    request: FlashcardGenerateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generates a new deck of intelligent AI flashcards from a topic or text source.
    """
    service = FlashcardsGenerationService(db)
    return await service.generate_and_save_flashcards(
        document_id=request.document_id, 
        owner_id=current_user.id,
        num_cards=request.num_cards,
        source_text=request.source_text,
        topic=request.topic
    )

@router.post("/{document_id}/flashcards", response_model=FlashcardDeckDetailResponse)
async def generate_flashcards(
    document_id: UUID,
    num_cards: int = 15,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generates a new deck of intelligent AI flashcards for a specific document.
    """
    service = FlashcardsGenerationService(db)
    return await service.generate_and_save_flashcards(
        document_id=document_id, 
        owner_id=current_user.id,
        num_cards=num_cards
    )

@router.get("/{document_id}/flashcards", response_model=List[FlashcardDeckResponse])
async def list_document_flashcard_decks(
    document_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Lists all flashcard decks previously generated for a specific document."""
    repo = FlashcardRepository(db)
    return repo.get_decks_by_document(document_id, current_user.id)

@router.get("/flashcards/decks/{deck_id}", response_model=FlashcardDeckDetailResponse)
async def get_flashcard_deck(
    deck_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Retrieves a specific flashcard deck and all its individual cards."""
    repo = FlashcardRepository(db)
    deck = repo.get_deck_by_id(deck_id, current_user.id)
    if not deck:
        raise HTTPException(status_code=404, detail="Flashcard deck not found")
    return deck
