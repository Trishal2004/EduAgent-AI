from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.analytics import Analytics, StudySession, QuizResult, Performance
from app.DTOs.analytics import (
    AnalyticsDashboardResponse, ScoresResponse, WeeklyProgressItem,
    SubjectRadarItem, QuickStatItem, RecommendationItem
)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def generate_dashboard(self, user_id: int) -> AnalyticsDashboardResponse:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)

        # Ensure Analytics profile exists
        profile = self.db.query(Analytics).filter(Analytics.user_id == user_id).first()
        if not profile:
            profile = Analytics(user_id=user_id)
            self.db.add(profile)
            self.db.commit()

        # 1. Weekly Progress (Last 7 Days)
        weekly_progress = []
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # We will mock the last 7 days dynamically based on actual data if available
        # But to match the 7 day chart, we iterate from 6 days ago to today
        for i in range(6, -1, -1):
            target_date = now - timedelta(days=i)
            day_name = days[target_date.weekday()]
            
            # Get study sessions for this day
            sessions = self.db.query(StudySession).filter(
                StudySession.user_id == user_id,
                func.date(StudySession.date) == target_date.date()
            ).all()
            
            hours = sum(s.duration_minutes for s in sessions) / 60.0
            
            # Get quiz results for this day
            quizzes = self.db.query(QuizResult).filter(
                QuizResult.user_id == user_id,
                func.date(QuizResult.date) == target_date.date()
            ).all()
            
            accuracy = 0
            if quizzes:
                accuracy = sum(q.accuracy_percentage for q in quizzes) / len(quizzes)
            elif i > 0 and len(weekly_progress) > 0:
                accuracy = weekly_progress[-1].accuracy # carry over last accuracy if 0 for visual smoothness
                
            weekly_progress.append(
                WeeklyProgressItem(name=day_name, hours=round(hours, 1), accuracy=round(accuracy, 1))
            )

        # 2. Subject Radar (Performance table)
        radar_items = []
        performances = self.db.query(Performance).filter(Performance.user_id == user_id).all()
        for p in performances:
            radar_items.append(SubjectRadarItem(
                subject=p.subject, strong=p.strong_score, weak=p.weak_score
            ))

        # 3. Quick Stats
        total_sessions = self.db.query(StudySession).filter(StudySession.user_id == user_id).all()
        total_hours = sum(s.duration_minutes for s in total_sessions) / 60.0
        
        all_quizzes = self.db.query(QuizResult).filter(QuizResult.user_id == user_id).all()
        avg_acc = sum(q.accuracy_percentage for q in all_quizzes) / len(all_quizzes) if all_quizzes else 0
        total_questions = sum(q.total_questions for q in all_quizzes)

        from app.models.question_paper import QuestionPaper
        from app.models.srs_flashcard import SRSDeck
        from app.models.note import Note
        
        total_papers = self.db.query(QuestionPaper).filter(QuestionPaper.owner_id == user_id).count()
        total_decks = self.db.query(SRSDeck).filter(SRSDeck.owner_id == user_id).count()
        total_notes = self.db.query(Note).filter(Note.owner_id == user_id).count()

        quick_stats = [
            QuickStatItem(label="Study Hours", value=f"{round(total_hours, 1)}h", icon_name="FiClock"),
            QuickStatItem(label="Quiz Accuracy", value=f"{round(avg_acc)}%", icon_name="FiTarget"),
            QuickStatItem(label="Questions Asked", value=str(total_questions), icon_name="FiActivity"),
            QuickStatItem(label="Notes Generated", value=str(total_notes), icon_name="FiFileText"),
            QuickStatItem(label="Cards Studied", value=str(total_decks), icon_name="FiBook"),
            QuickStatItem(label="Papers Created", value=str(total_papers), icon_name="FiAward")
        ]

        # 4. Scores
        scores = ScoresResponse(
            knowledge=round(min(100, avg_acc + 5)),
            learning=round(min(100, (total_hours / 10) * 100)), # mock formula
            revision=round(min(100, len(all_quizzes) * 10))
        )

        # 5. Recommendations
        recommendations = []
        weakest_subject = min(performances, key=lambda x: x.strong_score - x.weak_score, default=None)
        if weakest_subject:
            recommendations.append(RecommendationItem(
                type="Suggested Revision",
                title=f"{weakest_subject.subject} Fundamentals",
                desc="You struggled with this in your recent sessions.",
                icon_name="FiAlertCircle"
            ))
            recommendations.append(RecommendationItem(
                type="Suggested Quiz",
                title=f"{weakest_subject.subject} Practice",
                desc="Test your retention to build strength.",
                icon_name="FiTarget"
            ))
        else:
            recommendations.append(RecommendationItem(
                type="Suggested Reading",
                title="Keep it up!",
                desc="You are doing great across all subjects.",
                icon_name="FiBook"
            ))

        return AnalyticsDashboardResponse(
            scores=scores,
            weeklyProgress=weekly_progress,
            subjectRadar=radar_items,
            quickStats=quick_stats,
            recommendations=recommendations,
            streak=profile.current_streak,
            badges=profile.badges_earned or [
                "First document uploaded",
                "First quiz completed",
                "7-day streak",
                "30-day streak",
                "Flashcard expert",
                "Quiz master",
                "AI learner badge"
            ]
        )

    # Mutation methods for testing
    def log_study_session(self, user_id: int, subject: str, duration: int):
        s = StudySession(user_id=user_id, subject=subject, duration_minutes=duration)
        self.db.add(s)
        self.db.commit()

    def log_quiz_result(self, user_id: int, subject: str, score: float, total_questions: int):
        acc = (score / total_questions) * 100 if total_questions > 0 else 0
        q = QuizResult(user_id=user_id, subject=subject, score=score, total_questions=total_questions, accuracy_percentage=acc)
        self.db.add(q)
        self.db.commit()

    def update_performance(self, user_id: int, subject: str, strong: float, weak: float):
        p = self.db.query(Performance).filter(Performance.user_id == user_id, Performance.subject == subject).first()
        if p:
            p.strong_score = strong
            p.weak_score = weak
        else:
            p = Performance(user_id=user_id, subject=subject, strong_score=strong, weak_score=weak)
            self.db.add(p)
        self.db.commit()
