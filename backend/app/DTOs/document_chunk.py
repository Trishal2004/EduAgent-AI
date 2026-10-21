from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

class DocumentChunkCreate(BaseModel):
    document_id: UUID
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    text_content: str
    extracted_metadata: Optional[dict[str, Any]] = None

class ProcessingResponse(BaseModel):
    message: str
    document_id: UUID
    chunks_extracted: int
