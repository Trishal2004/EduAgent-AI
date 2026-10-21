from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, date
from enum import Enum

class QuestionTypeEnum(str, Enum):
    mcq = "mcq"
    short = "short"
    long = "long"
    coding = "coding"
    case_study = "case_study"

class DifficultyEnum(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

# -----------------
# For LLM Generation Structure
# -----------------
class GeneratedQuestion(BaseModel):
    question_type: QuestionTypeEnum = Field(..., description="The type of the question.")
    question_text: str = Field(..., description="The actual question.")
    options: Optional[List[str]] = Field(None, description="For MCQs only. Exactly 4 options.")
    correct_answer: str = Field(..., description="The exact correct answer (if MCQ, must exactly match one of the options).")
    explanation: str = Field(..., description="Why this answer is correct.")

class QuizGeneration(BaseModel):
    """Schema to force the LLM to output a list of questions."""
    questions: List[GeneratedQuestion] = Field(..., description="List of generated quiz questions.")

class AIGradedAnswer(BaseModel):
    question_id: str = Field(..., description="The ID of the question.")
    is_correct: bool = Field(..., description="True if the user's answer is conceptually correct, False otherwise.")

class AIGradingResponse(BaseModel):
    """Schema for bulk AI grading of text-based questions."""
    results: List[AIGradedAnswer] = Field(..., description="List of grading results.")

# -----------------
# For API Responses
# -----------------
class QuizQuestionPublicResponse(BaseModel):
    """Public version of a question without the correct answer."""
    id: UUID
    question_type: str
    question_text: str
    options: Optional[List[str]]
    
    model_config = {"from_attributes": True}

class QuizResponse(BaseModel):
    id: UUID
    document_id: Optional[UUID] = None
    owner_id: int
    topic: Optional[str] = None
    difficulty: str
    is_daily: bool = False
    quiz_date: Optional[date] = None
    quiz_number: Optional[int] = None
    status: str = "Not Started"
    created_at: datetime
    
    score: Optional[float] = None
    question_count: int = 0
    question_types: List[str] = []
    
    time_spent_seconds: Optional[int] = 0
    document_filename: Optional[str] = None
    
    model_config = {"from_attributes": True}

class QuizDetailResponse(QuizResponse):
    """Full quiz data returned to user to take the test."""
    questions: List[QuizQuestionPublicResponse]

class QuizSubmitRequest(BaseModel):
    """User submits answers as a dictionary of question_id -> answer_text"""
    answers: Dict[UUID, str]
    time_spent_seconds: Optional[int] = 0

class QuizGenerateRequest(BaseModel):
    """Payload for generating a new quiz."""
    document_id: Optional[UUID] = None
    topic: Optional[str] = None
    source_text: Optional[str] = None
    difficulty: DifficultyEnum = DifficultyEnum.medium
    number_of_questions: int = Field(10, ge=1, le=50)

class QuizAttemptResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    score: float
    total_questions: int
    time_spent_seconds: Optional[int] = 0
    completed_at: datetime
    
    model_config = {"from_attributes": True}
