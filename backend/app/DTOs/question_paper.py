from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class PaperPatternEnum(str, Enum):
    university = "university"
    mixed = "mixed"

# -----------------
# For LLM Generation Structure
# -----------------
class QuestionItem(BaseModel):
    question: str = Field(..., description="The actual question text.")
    marks: int = Field(..., description="Marks awarded for this question (e.g., 2, 5, or 10).")
    model_answer: str = Field(..., description="A detailed model answer or key points for grading this question.")

class Section(BaseModel):
    section_name: str = Field(..., description="Name of the section (e.g., 'Part A (2 Marks)').")
    instructions: str = Field(..., description="Instructions for this section (e.g., 'Answer all questions').")
    questions: List[QuestionItem] = Field(..., description="List of questions in this section.")

class QuestionPaperGeneration(BaseModel):
    title: str = Field(..., description="Title of the Question Paper.")
    sections: List[Section] = Field(..., description="Sections of the paper.")

# -----------------
# For API Responses
# -----------------
class QuestionPaperResponse(BaseModel):
    id: UUID
    document_id: UUID
    owner_id: UUID
    paper_type: str
    content_json: dict
    pdf_file_path: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True
