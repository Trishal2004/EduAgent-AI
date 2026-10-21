from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class NoteTypeEnum(str, Enum):
    short = "short"
    detailed = "detailed"
    revision = "revision"
    exam = "exam"
    interview = "interview"
    cheat_sheet = "cheat_sheet"

class StudyNoteGenerateRequest(BaseModel):
    note_type: NoteTypeEnum = Field(..., description="The type of note to generate")

class StudyNoteResponse(BaseModel):
    id: UUID
    document_id: UUID
    owner_id: UUID
    note_type: str
    content: str
    created_at: datetime
    
    class Config:
        orm_mode = True
