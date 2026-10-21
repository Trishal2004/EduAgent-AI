from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class DashboardStats(BaseModel):
    streak: int
    studyTime: str
    examCountdown: str
    subjectsCompleted: int
    totalDocuments: int
    totalFlashcards: int
    totalQuizzes: int

class SubjectProgress(BaseModel):
    name: str
    progress: int
    color: str

class RecentActivityItem(BaseModel):
    action: str
    subject: str
    detail: str
    time: str

class ChartDataPoint(BaseModel):
    day: str
    hours: float

class DashboardProfileBase(BaseModel):
    badges_earned: List[str] = []
    next_exam_date: Optional[datetime] = None

class DashboardProfileResponse(DashboardProfileBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class ContinueLearningItem(BaseModel):
    title: str
    type: str
    time: str

class RecommendationItem(BaseModel):
    title: str
    reason: str

class StudyPlanQuizItem(BaseModel):
    id: str
    topic: str
    difficulty: str
    status: str
    total_questions: int

class WeeklyStudyGoal(BaseModel):
    current_hours: float
    target_hours: float

class QuizPerformancePoint(BaseModel):
    date: str
    score: float
    accuracy: float

class DashboardResponse(BaseModel):
    username: str
    greeting: str
    stats: DashboardStats
    badges: List[str]
    recentActivity: List[RecentActivityItem]
    weeklyChartData: List[ChartDataPoint]
    subjectProgress: List[SubjectProgress]
    continueLearning: List[ContinueLearningItem]
    recommendations: List[RecommendationItem]
    studyPlanQuizzes: List[StudyPlanQuizItem]
    weeklyGoal: WeeklyStudyGoal
    quizPerformanceData: List[QuizPerformancePoint]
