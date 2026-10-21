from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SRSCardBase(BaseModel):
    question: str
    answer: str
    card_type: str
    difficulty: Optional[str] = 'medium'

class SRSCardCreate(SRSCardBase):
    pass

class ReviewHistoryResponse(BaseModel):
    id: int
    next_review_date: datetime
    last_reviewed: Optional[datetime]
    correct_answers: int
    wrong_answers: int
    review_count: int
    easiness_factor: float
    interval: int

    class Config:
        from_attributes = True

class SRSCardResponse(SRSCardBase):
    id: int
    deck_id: int
    created_at: datetime
    status: Optional[str] = 'new'
    review_history: Optional[ReviewHistoryResponse]

    class Config:
        from_attributes = True

class SRSDeckBase(BaseModel):
    title: str
    description: Optional[str] = None
    topic: Optional[str] = None
    document_id: Optional[str] = None
    is_favorite: Optional[bool] = False

class SRSDeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_favorite: Optional[bool] = None

class SRSDeckCreate(SRSDeckBase):
    cards: Optional[List[SRSCardCreate]] = []

class DeckGenerateRequest(BaseModel):
    topic: str
    card_type: str
    document_id: Optional[str] = None
    number_of_cards: Optional[int] = 5
    difficulty: Optional[str] = "medium"

class SRSDeckResponse(SRSDeckBase):
    id: int
    created_at: datetime
    cards: List[SRSCardResponse] = []
    
    # Calculated fields for frontend
    total_cards: Optional[int] = 0
    due_cards: Optional[int] = 0

    class Config:
        from_attributes = True

class ReviewScore(BaseModel):
    quality: int # 0 to 5 (0=Blackout, 1=Incorrect, 2=Hard, 3=Medium, 4=Good, 5=Easy)
