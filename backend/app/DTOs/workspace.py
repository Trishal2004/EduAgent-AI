from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class RecentFileResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    file_size: int
    last_opened_at: datetime
    
    model_config = {"from_attributes": True}

class PinnedDocumentResponse(BaseModel):
    id: UUID
    document_id: UUID
    filename: str
    pinned_at: datetime
    
    model_config = {"from_attributes": True}

class RecentActivityResponse(BaseModel):
    id: UUID
    activity_type: str
    description: str
    reference_id: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}

class RecentChatResponse(BaseModel):
    id: UUID
    title: str
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class WorkspaceDashboardResponse(BaseModel):
    recent_uploads: List[RecentFileResponse]
    pinned_files: List[PinnedDocumentResponse]
    last_opened_document: Optional[RecentFileResponse]
    recent_chats: List[RecentChatResponse]
    activities: List[RecentActivityResponse]
    
    model_config = {"from_attributes": True}
