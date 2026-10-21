from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class CardTypeEnum(str, Enum):
    definition = "definition"
    example = "example"
    formula = "formula"
    interview = "interview"
    true_false = "true_false"


# -----------------
# For LLM Generation Structure
# -----------------
class GeneratedFlashcard(BaseModel):
    card_type: CardTypeEnum = Field(..., description="The type of the card.")
    front: str = Field(..., description="The question or prompt on the front of the card.")
    back: str = Field(..., description="The answer or explanation on the back of the card.")


class FlashcardDeckGeneration(BaseModel):
    """Schema to force the LLM to output a list of cards."""
    cards: List[GeneratedFlashcard] = Field(..., description="List of generated flashcards.")


# -----------------
# For API Responses
# -----------------
class FlashcardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    deck_id: UUID
    card_type: str
    front: str
    back: str


class FlashcardDeckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: Optional[UUID] = None
    topic: Optional[str] = None
    owner_id: int
    created_at: datetime


class FlashcardDeckDetailResponse(FlashcardDeckResponse):
    model_config = ConfigDict(from_attributes=True)

    cards: List[FlashcardResponse]


class FlashcardGenerateRequest(BaseModel):
    document_id: Optional[UUID] = None
    topic: Optional[str] = None
    source_text: Optional[str] = None
    num_cards: int = Field(15, ge=1, le=100)
