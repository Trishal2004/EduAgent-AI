import asyncio
from app.models import user, document, tutor, note, flashcard, srs_flashcard, quiz, question_paper, knowledge_graph, analytics, mentor, workspace, course, notification, study_plan, otp
from app.db.database import SessionLocal
from app.services.tutor_service import TutorService

def main():
    db = SessionLocal()
    try:
        service = TutorService(db)
        history = service.get_history(user_id=1)
        print("Success:", len(history))
    except Exception as e:
        print("Error:", type(e).__name__, "-", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
