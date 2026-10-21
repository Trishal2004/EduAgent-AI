from pydantic import BaseModel
from typing import List, Optional

class ScoresResponse(BaseModel):
    knowledge: float
    learning: float
    revision: float

class WeeklyProgressItem(BaseModel):
    name: str
    hours: float
    accuracy: float

class SubjectRadarItem(BaseModel):
    subject: str
    strong: float
    weak: float

class QuickStatItem(BaseModel):
    label: str
    value: str
    icon_name: str # e.g. "FiClock"

class RecommendationItem(BaseModel):
    type: str
    title: str
    desc: str
    icon_name: str

class AnalyticsDashboardResponse(BaseModel):
    scores: ScoresResponse
    weeklyProgress: List[WeeklyProgressItem]
    subjectRadar: List[SubjectRadarItem]
    quickStats: List[QuickStatItem]
    recommendations: List[RecommendationItem]
    streak: int
    badges: List[str]

# Internal tracking models for manual API testing
class StudySessionCreate(BaseModel):
    subject: str
    duration_minutes: int

class QuizResultCreate(BaseModel):
    subject: str
    score: float
    total_questions: int
    
class PerformanceCreate(BaseModel):
    subject: str
    strong_score: float
    weak_score: float
