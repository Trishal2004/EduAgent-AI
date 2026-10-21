from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.security import deps
from app.models.user import User
from app.DTOs.notification import NotificationResponse, NotificationCreate
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = NotificationService(db)
    return service.get_user_notifications(current_user.id)

@router.post("", response_model=NotificationResponse)
def create_notification(
    notif_in: NotificationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = NotificationService(db)
    return service.create_notification(current_user.id, notif_in)

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = NotificationService(db)
    return service.mark_as_read(current_user.id, notification_id)

@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = NotificationService(db)
    return service.mark_all_read(current_user.id)
