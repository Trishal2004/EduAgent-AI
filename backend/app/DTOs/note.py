from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True

class FolderBase(BaseModel):
    name: str

class FolderResponse(FolderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    title: str
    topic: Optional[str] = None
    note_type: str
    content: str
    folder_id: Optional[int] = None
    document_id: Optional[str] = None
    tags: Optional[List[int]] = [] # Tag IDs

class NoteGenerateRequest(BaseModel):
    topic: str
    note_type: str
    folder_id: Optional[int] = None
    document_id: Optional[str] = None
    instructions: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    note_type: Optional[str] = None
    content: Optional[str] = None
    folder_id: Optional[int] = None
    document_id: Optional[str] = None
    tags: Optional[List[int]] = None
    is_favorite: Optional[bool] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    topic: Optional[str] = None
    note_type: str
    content: str
    is_favorite: bool
    folder_id: Optional[int]
    document_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True

class AINoteSection(BaseModel):
    title: str
    content: str

class AIGeneratedNote(BaseModel):
    title: str
    topic: str
    sections: List[AINoteSection]
    key_points: List[str]
    source_references: List[str]
