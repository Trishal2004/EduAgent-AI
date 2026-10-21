from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.models.processed_chunk import ProcessedChunk

db = SessionLocal()
doc_id = "2d2d89de-9a81-4d77-817b-a552940a82dd"
doc = db.query(Document).filter(Document.id == doc_id).first()
print(doc)
chunks = db.query(ProcessedChunk).filter(ProcessedChunk.document_id == doc_id).all()
print(len(chunks))
