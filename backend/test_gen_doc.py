import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.document import Document
from app.models.processed_chunk import ProcessedChunk
from app.config.config import settings
from app.services.gemini_service import GeminiService
from pydantic import BaseModel
from typing import List

class AIFlashcard(BaseModel):
    question: str
    answer: str
    difficulty: str

class AIFlashcardList(BaseModel):
    cards: List[AIFlashcard]

def test():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    doc = db.query(Document).filter(Document.filename.like('%Optical%')).first()
    chunks = db.query(ProcessedChunk).filter(ProcessedChunk.document_id == doc.id).order_by(ProcessedChunk.page_number, ProcessedChunk.chunk_index).all()
    full_text = "\n\n".join([chunk.text_content for chunk in chunks])
    if len(full_text) > 400000:
        full_text = full_text[:400000] + "\n\n[DOCUMENT TRUNCATED DUE TO LENGTH LIMITS]"
    
    system_prompt = f"You are an expert tutor. Create exactly 5 high-quality flashcards based ONLY on the provided document context. The target difficulty for these cards is easy. Focus on the topic: principal of optical fibers."
    user_prompt = f"Card Type: definition\n\nDocument Context:\n{full_text}"
    
    print("Sending to Gemini... Text length:", len(full_text))
    svc = GeminiService()
    try:
        res = svc.generate_json(system_prompt, user_prompt, AIFlashcardList)
        print("Success:", len(res.get('cards', [])))
    except Exception as e:
        print("Error generating:", type(e).__name__, str(e))

if __name__ == "__main__":
    test()
