from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.dashboard import DashboardProfile
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import QuizAttempt
from app.models.analytics import Analytics, StudySession, Performance
from app.models.workspace import RecentActivity, RecentFile

class DashboardRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_profile(self, user_id: int) -> DashboardProfile:
        profile = self.session.query(DashboardProfile).filter(DashboardProfile.user_id == user_id).first()
        if not profile:
            profile = DashboardProfile(user_id=user_id, badges_earned=["Early Adopter"], next_exam_date=None)
            self.session.add(profile)
            self.session.commit()
            self.session.refresh(profile)
        return profile

    def count_documents(self, user_id: int) -> int:
        return self.session.query(Document).filter(Document.owner_id == user_id).count()

    def count_flashcards(self, user_id: int) -> int:
        from app.models.flashcard import FlashcardDeck
        return self.session.query(Flashcard).join(FlashcardDeck).filter(FlashcardDeck.owner_id == user_id).count()

    def count_quizzes(self, user_id: int) -> int:
        return self.session.query(QuizAttempt).filter(QuizAttempt.owner_id == user_id).count()

    def get_analytics(self, user_id: int) -> Analytics:
        analytics = self.session.query(Analytics).filter(Analytics.user_id == user_id).first()
        if not analytics:
            analytics = Analytics(user_id=user_id, current_streak=0, total_study_hours=0.0)
            self.session.add(analytics)
            self.session.commit()
            self.session.refresh(analytics)
        return analytics

    def get_recent_activities(self, user_id: int, limit: int = 5):
        from app.models.workspace import Workspace
        workspace = self.session.query(Workspace).filter(Workspace.owner_id == user_id).first()
        if not workspace:
            return []
        return self.session.query(RecentActivity).filter(RecentActivity.workspace_id == workspace.id).order_by(desc(RecentActivity.created_at)).limit(limit).all()

    def get_performances(self, user_id: int):
        return self.session.query(Performance).filter(Performance.user_id == user_id).all()

    def get_study_sessions(self, user_id: int, days: int = 7):
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.session.query(StudySession).filter(StudySession.user_id == user_id, StudySession.date >= cutoff).all()

    def get_recent_files(self, user_id: int, limit: int = 3):
        from app.models.workspace import Workspace
        workspace = self.session.query(Workspace).filter(Workspace.owner_id == user_id).first()
        if not workspace:
            return []
        return self.session.query(RecentFile).filter(RecentFile.workspace_id == workspace.id).order_by(desc(RecentFile.last_opened_at)).limit(limit).all()

    def update_profile(self, user_id: int, badges_earned: list, next_exam_date) -> DashboardProfile:
        profile = self.get_profile(user_id)
        profile.badges_earned = badges_earned
        profile.next_exam_date = next_exam_date
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def get_daily_quizzes(self, user_id: int, limit: int = 3):
        from app.models.quiz import Quiz
        from datetime import date
        today = date.today()
        # First try to get today's daily quizzes
        quizzes = self.session.query(Quiz).filter(
            Quiz.owner_id == user_id, 
            Quiz.is_daily == True,
            Quiz.quiz_date == today
        ).limit(limit).all()
        
        if not quizzes:
            # Fallback: get recent incomplete quizzes
            quizzes = self.session.query(Quiz).filter(
                Quiz.owner_id == user_id,
                Quiz.status != "Completed"
            ).order_by(desc(Quiz.created_at)).limit(limit).all()
            
        return quizzes

    def get_weekly_goal(self, user_id: int):
        from app.models.study_plan import StudyPlan
        from datetime import datetime, timedelta
        import sqlalchemy.exc
        
        target_hours = 10.0
        try:
            study_plan = self.session.query(StudyPlan).filter(StudyPlan.user_id == user_id).order_by(desc(StudyPlan.created_at)).first()
            if study_plan and hasattr(study_plan, 'daily_hours'):
                target_hours = float(study_plan.daily_hours * 7)
        except sqlalchemy.exc.OperationalError:
            # Table schema mismatch or table missing
            self.session.rollback()
            pass
            
        cutoff = datetime.utcnow() - timedelta(days=7)
        sessions = self.session.query(StudySession).filter(
            StudySession.user_id == user_id, 
            StudySession.date >= cutoff
        ).all()
        
        current_hours = sum([session.duration_minutes / 60.0 for session in sessions])
        return {"current_hours": current_hours, "target_hours": target_hours}

    def get_recent_quiz_results(self, user_id: int, limit: int = 7):
        from app.models.analytics import QuizResult
        return self.session.query(QuizResult).filter(QuizResult.user_id == user_id).order_by(desc(QuizResult.date)).limit(limit).all()

