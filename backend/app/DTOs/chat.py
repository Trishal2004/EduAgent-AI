from pydantic import BaseModel, Field
from typing import List, Optional

class Citation(BaseModel):
    document_id: Optional[str] = Field(None, description="The UUID of the source document")
    page_number: Optional[int] = Field(None, description="The page number where the information was found")
    section_title: Optional[str] = Field(None, description="The title of the section")

class StructuredAnswer(BaseModel):
    """
    Highly detailed, structured educational response.
    The LLM MUST fill out all of these fields comprehensively.
    """
    definition: str = Field(..., description="A clear, academic definition of the core concept.")
    simple_explanation: str = Field(..., description="A layman's explanation, easy for a beginner to understand.")
    detailed_explanation: str = Field(..., description="A deep, comprehensive explanation of how it works.")
    real_world_example: str = Field(..., description="A practical, real-world example illustrating the concept.")
    advantages: List[str] = Field(..., description="A list of pros or advantages.")
    disadvantages: List[str] = Field(..., description="A list of cons or disadvantages.")
    applications: List[str] = Field(..., description="Common use cases or applications.")
    interview_questions: List[str] = Field(..., description="2-3 potential interview questions about this topic.")
    exam_tips: List[str] = Field(..., description="Tips for a student studying this for an exam.")
    related_topics: List[str] = Field(..., description="2-3 related concepts the user should explore.")
    citations: List[Citation] = Field(..., description="The exact sources used to generate this answer.")
    confidence_score: int = Field(..., description="An integer from 0 to 100 representing confidence in the answer accuracy based on context.")

class ChatRequest(BaseModel):
    question: str
