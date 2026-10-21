import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.db.database import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.DTOs.srs_flashcard import DeckGenerateRequest
from app.controllers.srs_flashcards import generate_deck
import uuid

async def test():
    db = SessionLocal()
    # Get any user
    user = db.query(User).first()
    if not user:
        print("No users found.")
        return
    
    # Get a processed document for this user
    doc = db.query(Document).filter(Document.owner_id == user.id, Document.upload_status == 'completed').first()
    doc_id = str(doc.id) if doc else None
    
    print(f"Testing with user={user.email}, doc_id={doc_id}")
    
    req = DeckGenerateRequest(
        topic="Laser and Optical Fibers",
        card_type="definition",
        number_of_cards=10,
        difficulty="medium",
        document_id=doc_id
    )
    
    try:
        res = await generate_deck(request=req, db=db, current_user=user)
        print("SUCCESS:")
        print(res)
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {str(e)}")
        if hasattr(e, 'detail'):
            print(f"Detail: {e.detail}")

if __name__ == "__main__":
    asyncio.run(test())
