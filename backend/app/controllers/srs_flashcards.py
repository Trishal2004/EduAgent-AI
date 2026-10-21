from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from app.security import deps
from app.models.user import User
from app.DTOs.srs_flashcard import SRSDeckCreate, SRSDeckResponse, SRSCardCreate, SRSCardResponse, ReviewScore, DeckGenerateRequest, SRSDeckUpdate
from app.services.flashcard_service import SRSFlashcardService
from app.services.gemini_service import GeminiService
from app.config.config import settings
import json

router = APIRouter()

@router.get("/decks", response_model=List[SRSDeckResponse])
def get_decks(db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    return service.get_decks(current_user.id)

@router.post("/decks", response_model=SRSDeckResponse)
def create_deck(deck_in: SRSDeckCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    return service.create_deck(current_user.id, deck_in)

class AIFlashcard(BaseModel):
    question: str
    answer: str
    difficulty: str

class AIFlashcardList(BaseModel):
    cards: List[AIFlashcard]

@router.post("/decks/generate", response_model=SRSDeckResponse)
async def generate_deck(request: DeckGenerateRequest, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    gemini_service = GeminiService()
    
    num_cards = request.number_of_cards or 5
    target_difficulty = request.difficulty or "medium"
    
    if request.document_id:
        from app.models.document import Document
        from app.models.processed_chunk import ProcessedChunk
        
        doc = db.query(Document).filter(Document.id == request.document_id, Document.owner_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Selected document could not be found.")
        if doc.upload_status != "completed":
            raise HTTPException(status_code=400, detail="Please process this document before generating flashcards.")
            
        chunks = db.query(ProcessedChunk).filter(ProcessedChunk.document_id == request.document_id).order_by(ProcessedChunk.page_number, ProcessedChunk.chunk_index).all()
        if not chunks:
            raise HTTPException(status_code=400, detail="No text chunks found for this document")
            
        full_text = "\n\n".join([chunk.text_content for chunk in chunks])
        if len(full_text) > 400000:
            full_text = full_text[:400000] + "\n\n[DOCUMENT TRUNCATED DUE TO LENGTH LIMITS]"
        
        system_prompt = f"You are an expert tutor. Create exactly {num_cards} high-quality flashcards based ONLY on the provided document context. The target difficulty for these cards is {target_difficulty}. Focus on the topic: {request.topic}."
        user_prompt = f"Card Type: {request.card_type}\n\nDocument Context:\n{full_text}"
        
        try:
            ai_response_dict = gemini_service.generate_json(system_prompt, user_prompt, AIFlashcardList)
            ai_response = AIFlashcardList(**ai_response_dict)
            if not ai_response.cards:
                raise HTTPException(status_code=500, detail="The AI returned an invalid flashcard response.")
        except Exception as e:
            error_str = str(e)
            if "Gemini API Key is missing" in error_str or "API key not valid" in error_str:
                raise HTTPException(status_code=500, detail="AI service authentication failed. Check the backend API key.")
            elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                raise HTTPException(status_code=429, detail="AI service rate limit reached. Please try again later.")
            else:
                raise HTTPException(status_code=500, detail="The AI returned an invalid flashcard response.")
                
        cards = [SRSCardCreate(question=c.question, answer=c.answer, card_type=request.card_type, difficulty=c.difficulty) for c in ai_response.cards]
            
        deck_in = SRSDeckCreate(
            title=f"Flashcards: {doc.filename}",
            description=f"Generated {request.card_type} cards from document.",
            topic=request.topic,
            document_id=request.document_id,
            cards=cards
        )
        return service.create_deck(current_user.id, deck_in)

    # If no document provided, generate from general knowledge
    system_prompt = f"You are an expert tutor. Create exactly {num_cards} high-quality flashcards for the given topic. The target difficulty is {target_difficulty}."
    user_prompt = f"Topic: {request.topic}\nCard Type: {request.card_type}"
    
    try:
        ai_response_dict = gemini_service.generate_json(system_prompt, user_prompt, AIFlashcardList)
        ai_response = AIFlashcardList(**ai_response_dict)
        if not ai_response.cards:
            raise HTTPException(status_code=500, detail="The AI returned an invalid flashcard response.")
    except Exception as e:
        error_str = str(e)
        if "Gemini API Key is missing" in error_str or "API key not valid" in error_str:
            raise HTTPException(status_code=500, detail="AI service authentication failed. Check the backend API key.")
        elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            raise HTTPException(status_code=429, detail="AI service rate limit reached. Please try again later.")
        else:
            raise HTTPException(status_code=500, detail="The AI returned an invalid flashcard response.")
            
    cards = [SRSCardCreate(question=c.question, answer=c.answer, card_type=request.card_type, difficulty=c.difficulty) for c in ai_response.cards]
        
    deck_in = SRSDeckCreate(
        title=request.topic,
        description=f"Generated {request.card_type} cards",
        topic=request.topic,
        cards=cards
    )
    
    return service.create_deck(current_user.id, deck_in)

@router.delete("/decks/{deck_id}")
def delete_deck(deck_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    service.delete_deck(current_user.id, deck_id)
    return {"status": "success", "message": "Deck deleted successfully"}

@router.put("/decks/{deck_id}", response_model=SRSDeckResponse)
def update_deck(deck_id: int, deck_in: SRSDeckUpdate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    return service.update_deck(current_user.id, deck_id, deck_in)

@router.post("/decks/{deck_id}/cards", response_model=SRSCardResponse)
def add_card(deck_id: int, card_in: SRSCardCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    return service.add_card(current_user.id, deck_id, card_in)

@router.delete("/cards/{card_id}")
def delete_card(card_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    service.delete_card(current_user.id, card_id)
    return {"status": "success"}

@router.get("/decks/{deck_id}/review", response_model=List[SRSCardResponse])
def get_due_cards(deck_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    return service.get_due_cards(current_user.id, deck_id)

@router.post("/cards/{card_id}/review")
def review_card(card_id: int, score: ReviewScore, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = SRSFlashcardService(db)
    return service.save_score(current_user.id, card_id, score.quality)
