from sqlalchemy.orm import Session
from typing import List
from app.models.processed_chunk import ProcessedChunk
from app.DTOs.processed_chunk import ProcessedChunkCreate

class ProcessedChunkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_many(self, chunks: List[ProcessedChunkCreate]) -> None:
        """Bulk inserts many processed semantic chunks into the database."""
        if not chunks:
            return
            
        db_chunks = [
            ProcessedChunk(
                document_id=chunk.document_id,
                parent_chunk_id=chunk.parent_chunk_id,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                chunk_index=chunk.chunk_index,
                text_content=chunk.text_content,
                embedding=chunk.embedding
            )
            for chunk in chunks
        ]
        
        self.session.add_all(db_chunks)
        self.session.commit()
