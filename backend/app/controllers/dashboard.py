from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.security import deps
from app.models.user import User
from app.DTOs.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()

@router.get("/metrics", response_model=DashboardResponse)
def get_dashboard_metrics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retrieve comprehensive dashboard data for the current user.
    """
    service = DashboardService(db)
    return service.generate_dashboard(current_user)
