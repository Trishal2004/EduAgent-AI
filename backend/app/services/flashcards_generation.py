from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import HTTPException
from uuid import UUID
from typing import Optional
from google import genai
import json
from app.models.document import Document
from app.models.processed_chunk import ProcessedChunk
from app.repositories.flashcard import FlashcardRepository
from app.DTOs.flashcard import FlashcardDeckGeneration
from app.config.config import settings

class FlashcardsGenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.flashcard_repo = FlashcardRepository(db)

    async def generate_and_save_flashcards(self, document_id: Optional[UUID], owner_id: int, num_cards: int = 15, source_text: Optional[str] = None, topic: Optional[str] = None):
        if not settings.GEMINI_API_KEY:
            raise HTTPException(status_code=400, detail="Gemini API Key is missing. Please configure a real key in .env.")
            
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        full_text = ""
        
        if source_text:
            full_text = source_text
        elif document_id:
            # 1. Verify document
            doc_result = self.db.execute(select(Document).where(Document.id == document_id, Document.owner_id == owner_id))
            doc = doc_result.scalars().first()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")
            if doc.upload_status != "completed":
                raise HTTPException(status_code=400, detail="Document has not been processed yet")
    
            # 2. Gather Document Context
            chunk_result = self.db.execute(
                select(ProcessedChunk)
                .where(ProcessedChunk.document_id == document_id)
                .order_by(ProcessedChunk.page_number, ProcessedChunk.chunk_index)
            )
            chunks = chunk_result.scalars().all()
            
            if not chunks:
                raise HTTPException(status_code=400, detail="No text chunks found for this document")
    
            full_text = "\n\n".join([chunk.text_content for chunk in chunks])
            if len(full_text) > 400000:
                full_text = full_text[:400000] + "\n\n[DOCUMENT TRUNCATED DUE TO LENGTH LIMITS]"
        else:
            if not topic:
                raise HTTPException(status_code=400, detail="Must provide either a document, source text, or topic.")
            full_text = f"General knowledge regarding the topic: {topic}"
        
        system_prompt = f"You are an expert educator. Extract exactly {num_cards} flashcards from the provided document text. You MUST generate a mix of the following types: definition, example, formula, interview (Q&A), and true_false. Ensure the front of the card is a clear prompt or question, and the back is the accurate answer."
        
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=f"System: {system_prompt}\n\nUser: Document Text:\n{full_text}",
                config={"response_mime_type": "application/json", "response_schema": FlashcardDeckGeneration}
            )
            response_obj = FlashcardDeckGeneration(**json.loads(response.text))
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                raise HTTPException(status_code=429, detail="Gemini API rate limit exceeded (Free Tier). Please wait about 1 minute and try again.")
            raise HTTPException(status_code=500, detail=f"Gemini API Error: {error_str}")
        
        if not response_obj or not response_obj.cards:
            raise HTTPException(status_code=500, detail="Failed to generate flashcards")

        # 4. Save to Database
        saved_deck = self.flashcard_repo.create_deck(
            document_id=document_id,
            owner_id=owner_id,
            generated_cards=response_obj.cards,
            topic=topic
        )
        
        return saved_deck
