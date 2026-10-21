from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.security import deps
from app.models.user import User
from app.DTOs.mentor import MentorDashboardResponse, MentorChatResponse, ChatMessageRequest
from app.services.mentor_service import MentorService

router = APIRouter()

@router.get("/dashboard", response_model=MentorDashboardResponse)
def get_mentor_dashboard(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retrieves the mentor dashboard data (goals, weak topics, study plans).
    """
    service = MentorService(db)
    return service.get_dashboard(current_user.id)

@router.post("/generate", response_model=MentorDashboardResponse)
def generate_mentor_insights(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Triggers the AI Academic Mentor to generate new insights.
    """
    service = MentorService(db)
    return service.generate_insights(current_user.id)

@router.post("/chat", response_model=MentorChatResponse)
def send_mentor_message(
    request: ChatMessageRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Sends a chat message to the Mentor and gets an AI response.
    """
    service = MentorService(db)
    return service.process_chat(current_user.id, request)

@router.get("/chat/history", response_model=List[MentorChatResponse])
def get_mentor_chat_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retrieves mentor chat history.
    """
    service = MentorService(db)
    return service.get_chat_history(current_user.id)
