import sys
sys.path.append("/Users/k.trishal/Desktop/EduAgent AI/backend")
from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.models.quiz import QuizAttempt, Quiz
from app.models.analytics import Analytics, QuizResult, StudySession, Performance
from app.models.workspace import RecentActivity, RecentFile

def check():
    db = SessionLocal()
    user = db.query(User).first()
    print("Documents:", db.query(Document).filter_by(owner_id=user.id).count())
    print("Quizzes:", db.query(Quiz).filter_by(owner_id=user.id).count())
    print("Quiz Attempts:", db.query(QuizAttempt).filter_by(owner_id=user.id).count())
    print("Analytics Quiz Results:", db.query(QuizResult).filter_by(user_id=user.id).count())
    print("Analytics Study Sessions:", db.query(StudySession).filter_by(user_id=user.id).count())
    print("Analytics Performance:", db.query(Performance).filter_by(user_id=user.id).count())
    print("Recent Activities:", db.query(RecentActivity).count())
    print("Recent Files:", db.query(RecentFile).count())

check()
