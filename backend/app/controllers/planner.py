from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.security import deps
from app.models.user import User
from app.DTOs.planner import PlannerGenerateRequest, PlannerResponse
from app.services.planner_service import PlannerService

router = APIRouter()

@router.post("/generate", response_model=PlannerResponse)
async def generate_plan(
    request: PlannerGenerateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = PlannerService(db)
    return await service.generate_plan(current_user.id, request)

@router.get("", response_model=PlannerResponse)
def get_plan(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = PlannerService(db)
    plan = service.get_plan(current_user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan found")
    return plan
