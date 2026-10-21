from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class ProcessedChunkCreate(BaseModel):
    document_id: UUID
    parent_chunk_id: UUID
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_index: int
    text_content: str
    embedding: Optional[List[float]] = None
