from sqlalchemy.orm import Session
from typing import List
from app.models.document_chunk import DocumentChunk
from app.DTOs.document_chunk import DocumentChunkCreate

class DocumentChunkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_many(self, chunks: List[DocumentChunkCreate]) -> None:
        """Bulk inserts many chunks into the database."""
        if not chunks:
            return
            
        db_chunks = [
            DocumentChunk(
                document_id=chunk.document_id,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                text_content=chunk.text_content,
                extracted_metadata=chunk.extracted_metadata
            )
            for chunk in chunks
        ]
        
        self.session.add_all(db_chunks)
        self.session.commit()
