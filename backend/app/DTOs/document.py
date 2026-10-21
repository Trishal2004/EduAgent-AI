from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class PDFMetadataResponse(BaseModel):
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    page_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: UUID
    owner_id: int
    filename: str
    file_size: int
    content_type: str
    upload_status: str
    embedding_status: str = "unprocessed"
    created_at: datetime
    metadata_info: Optional[PDFMetadataResponse] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "owner_id": "987e6543-e21b-34d1-b654-426614174999",
                "filename": "lecture_slides.pdf",
                "file_size": 1048576,
                "content_type": "application/pdf",
                "upload_status": "uploaded",
                "embedding_status": "unprocessed",
                "created_at": "2023-10-27T10:00:00Z"
            }
        }
    )

class DocumentRenameRequest(BaseModel):
    new_name: str
