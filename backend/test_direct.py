import asyncio
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.document_processing import DocumentProcessingService
from uuid import UUID

async def main():
    db = SessionLocal()
    try:
        service = DocumentProcessingService(db)
        doc_id = UUID("b472db4a-b844-4ab7-9437-339845493373")
        # I don't remember the user_id, let's use 1
        # wait, process_document takes `document_id, owner_id`
        # in the API it takes owner_id as an int, but the type hint in document_processing.py says owner_id: UUID
        res = await service.process_document(doc_id, 1)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

asyncio.run(main())
