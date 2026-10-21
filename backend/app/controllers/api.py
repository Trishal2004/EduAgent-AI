from fastapi import APIRouter
from app.security import auth
from app.controllers import document, qdrant_test, tutor, flashcards, quizzes, question_papers, mentor, analytics, dashboard, courses, general_notes, srs_flashcards, knowledge_graph, workspace, search, notifications, planner

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(document.router, prefix="/documents", tags=["Documents"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["Workspace"])
api_router.include_router(qdrant_test.router, prefix="/qdrant-test", tags=["Qdrant Testing"])
api_router.include_router(tutor.router, prefix="/tutor", tags=["AI Tutor"])
api_router.include_router(courses.router, prefix="/courses", tags=["Course Management"])
api_router.include_router(general_notes.router, prefix="/notes", tags=["Organized Notes"])
# api_router.include_router(flashcards.router, prefix="/documents", tags=["Flashcards"]) # Deprecated: Unifying around SRS
api_router.include_router(srs_flashcards.router, prefix="/srs", tags=["Spaced Repetition Flashcards"])
api_router.include_router(quizzes.router, tags=["Quizzes"]) # Note: handles documents prefix inside router paths
api_router.include_router(question_papers.router, tags=["Question Papers"])
api_router.include_router(mentor.router, prefix="/mentor", tags=["AI Academic Mentor"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Learning Analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(knowledge_graph.router, prefix="/kg", tags=["Knowledge Graph"])
api_router.include_router(search.router, prefix="/search", tags=["Global Search"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(planner.router, prefix="/planner", tags=["Planner"])

from fastapi import Depends
from sqlalchemy.orm import Session
from app.security import deps
from sqlalchemy import text

@api_router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(deps.get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "detail": str(e)}
