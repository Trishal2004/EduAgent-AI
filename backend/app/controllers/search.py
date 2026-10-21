from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.security import deps
from app.models.user import User
from app.DTOs.search import GlobalSearchResponse
from app.services.search_service import GlobalSearchService

router = APIRouter()

@router.get("", response_model=GlobalSearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Search query string"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = GlobalSearchService(db)
    return service.search_all(current_user.id, q)
