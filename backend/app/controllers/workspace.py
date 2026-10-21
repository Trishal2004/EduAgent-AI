from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.security import deps
from app.models.user import User
from app.DTOs.workspace import WorkspaceDashboardResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter()

@router.get("/", response_model=WorkspaceDashboardResponse)
def get_workspace_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get aggregated data for the workspace dashboard.
    """
    service = WorkspaceService(db)
    return service.get_dashboard_data(current_user.id)
