from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.security import deps
from app.models.user import User
from app.DTOs.tutor import ChatRequest, ChatResponse, TutorSessionResponse
from app.services.tutor_service import TutorService
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

class RenameRequest(BaseModel):
    title: str

from app.config.config import settings

router = APIRouter()

@router.get("/history", response_model=List[TutorSessionResponse])
def get_tutor_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = TutorService(db)
    return service.get_history(int(current_user.id))

@router.get("/session/{session_id}", response_model=TutorSessionResponse)
def get_tutor_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = TutorService(db)
    return service.get_session(session_id, int(current_user.id))

@router.post("/session", response_model=TutorSessionResponse)
def create_empty_tutor_session(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = TutorService(db)
    return service.create_empty_session(int(current_user.id))

@router.delete("/session/all")
def delete_all_tutor_sessions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = TutorService(db)
    return service.delete_all_sessions(int(current_user.id))

@router.put("/session/{session_id}/rename", response_model=TutorSessionResponse)
def rename_tutor_session(
    session_id: str,
    request: RenameRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = TutorService(db)
    return service.rename_session(session_id, int(current_user.id), request.title)

@router.delete("/session/{session_id}")
def delete_tutor_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = TutorService(db)
    return service.delete_session(session_id, int(current_user.id))

@router.post("/chat")
async def chat_with_tutor(
    request: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    print("[AI TUTOR] Request received (Streaming)")
    service = TutorService(db)
    
    async def event_generator():
        try:
            async for chunk in service.chat_stream(request, int(current_user.id)):
                yield chunk
        except Exception as e:
            import json
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': 'An internal server error occurred'})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
