from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    document_id: Optional[str] = None
    question: str
    image_data: Optional[str] = None

class Citation(BaseModel):
    name: str
    page: int
    section: str
    confidence: str

class StructuredAnswer(BaseModel):
    topic: str
    definition: str
    beginner: str
    analogy: str
    example: str
    diagram: str
    keyPoints: List[str]
    advantages: str
    disadvantages: str
    interview: List[str]
    examTips: str
    mistakes: str
    summary: str
    related: List[str]
    citations: List[Citation]
    suggested: List[str]

class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TutorSessionResponse(BaseModel):
    id: str
    owner_id: int
    title: str
    document_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: Optional[List[ChatMessageResponse]] = []

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    session_id: str
    user_message: ChatMessageResponse
    ai_message: ChatMessageResponse
