import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.document import Document
from app.models.processed_chunk import ProcessedChunk
from app.config.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

doc = db.query(Document).filter(Document.filename.like('%Optical%')).first()
if doc:
    print(f"Found Doc: {doc.id}, {doc.filename}, status: {doc.upload_status}")
    chunks = db.query(ProcessedChunk).filter(ProcessedChunk.document_id == doc.id).all()
    print(f"Chunks: {len(chunks)}")
else:
    print("Document not found in DB")
