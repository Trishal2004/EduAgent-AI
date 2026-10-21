from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.security import deps
from app.models.user import User
from app.DTOs.analytics import (
    AnalyticsDashboardResponse, StudySessionCreate,
    QuizResultCreate, PerformanceCreate
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
def get_analytics_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Computes and returns all analytics data for the user's dashboard.
    This includes global metrics, progress charts, and activity heatmaps.
    """
    service = AnalyticsService(db)
    return service.generate_dashboard(current_user.id)

@router.post("/session")
def log_study_session(
    request: StudySessionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = AnalyticsService(db)
    service.log_study_session(current_user.id, request.subject, request.duration_minutes)
    return {"status": "success"}

@router.post("/quiz-result")
def log_quiz_result(
    request: QuizResultCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = AnalyticsService(db)
    service.log_quiz_result(current_user.id, request.subject, request.score, request.total_questions)
    return {"status": "success"}

@router.post("/performance")
def update_performance(
    request: PerformanceCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = AnalyticsService(db)
    service.update_performance(current_user.id, request.subject, request.strong_score, request.weak_score)
    return {"status": "success"}
