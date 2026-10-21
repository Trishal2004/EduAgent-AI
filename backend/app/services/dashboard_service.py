from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.repositories.dashboard import DashboardRepository
from app.DTOs.dashboard import (
    DashboardResponse, DashboardStats, SubjectProgress,
    RecentActivityItem, ChartDataPoint,
    ContinueLearningItem, RecommendationItem,
    StudyPlanQuizItem, WeeklyStudyGoal, QuizPerformancePoint
)
from app.models.user import User

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DashboardRepository(db)

    def get_greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning"
        elif hour < 17:
            return "Good Afternoon"
        else:
            return "Good Evening"

    def generate_dashboard(self, current_user: User) -> DashboardResponse:
        from app.models.quiz import QuizAttempt, Quiz
        from app.models.document import Document
        from app.models.note import Note
        from sqlalchemy import desc, func
        
        profile = self.repo.get_profile(current_user.id)
        
        # Base counts
        total_docs = self.db.query(Document).filter(Document.owner_id == current_user.id).count()
        total_quizzes = self.db.query(QuizAttempt).filter(QuizAttempt.owner_id == current_user.id).count()
        
        # 1. Total Study Time (from QuizAttempts time_spent_seconds)
        total_seconds = self.db.query(func.sum(QuizAttempt.time_spent_seconds)).filter(QuizAttempt.owner_id == current_user.id).scalar() or 0
        study_hours = int(total_seconds // 3600)
        study_mins = int((total_seconds % 3600) // 60)
        study_time_str = f"{study_hours}h {study_mins}m"
        
        # 2. Streak Calculation (Consecutive days with a QuizAttempt backwards from today)
        attempts_dates = self.db.query(func.date(QuizAttempt.completed_at)).filter(QuizAttempt.owner_id == current_user.id).distinct().order_by(desc(func.date(QuizAttempt.completed_at))).all()
        streak = 0
        today = datetime.utcnow().date()
        date_set = {d[0] for d in attempts_dates}
        
        current_check_date = today
        if current_check_date in date_set:
            streak += 1
            current_check_date -= timedelta(days=1)
        elif (current_check_date - timedelta(days=1)) in date_set:
            # They haven't studied today, but they studied yesterday. Keep counting from yesterday.
            current_check_date -= timedelta(days=1)
            streak += 1
            current_check_date -= timedelta(days=1)
            
        while current_check_date in date_set:
            streak += 1
            current_check_date -= timedelta(days=1)
            
        # Exam Countdown
        exam_countdown = "Not set"
        if profile.next_exam_date:
            days = (profile.next_exam_date.replace(tzinfo=None) - datetime.utcnow()).days
            exam_countdown = f"{days} Days" if days >= 0 else "Passed"

        stats = DashboardStats(
            streak=streak,
            studyTime=study_time_str,
            examCountdown=exam_countdown,
            subjectsCompleted=min(total_docs, 3), # Proxy for now
            totalDocuments=total_docs,
            totalFlashcards=0, # Stubbed for now, Flashcard logic is separate
            totalQuizzes=total_quizzes
        )

        # 3. Subject Progress (Real Quiz Attempt averages by Topic)
        topic_avg_scores = self.db.query(Quiz.topic, func.avg(QuizAttempt.score)).join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id).filter(Quiz.owner_id == current_user.id).group_by(Quiz.topic).all()
        
        subject_progress = []
        recommendations = []
        colors = ['bg-blue-500', 'bg-emerald-500', 'bg-indigo-500', 'bg-purple-500']
        
        weakest_topic = None
        lowest_score = 101.0
        
        for idx, (topic, avg_score) in enumerate(topic_avg_scores):
            topic_name = topic or "General Knowledge"
            score_val = min(100, int(avg_score))
            subject_progress.append(
                SubjectProgress(name=topic_name, progress=score_val, color=colors[idx % len(colors)])
            )
            if score_val < lowest_score:
                lowest_score = score_val
                weakest_topic = topic_name
                
        if weakest_topic and lowest_score < 70:
            recommendations.append(
                RecommendationItem(title=f"Review {weakest_topic}", reason=f"Your average score is {lowest_score}%. A quick review could help!")
            )
        else:
            recommendations.append(RecommendationItem(title="Keep it up!", reason="Your scores are looking great across all subjects."))

        # 4. Weekly Chart Data (Real quiz time spent per day over last 7 days)
        chart_dict = {}
        for i in range(6, -1, -1):
            d = (datetime.utcnow() - timedelta(days=i)).strftime("%a")
            chart_dict[d] = 0.0
            
        cutoff = datetime.utcnow() - timedelta(days=7)
        recent_attempts = self.db.query(QuizAttempt).filter(QuizAttempt.owner_id == current_user.id, QuizAttempt.completed_at >= cutoff).all()
        
        for att in recent_attempts:
            day_str = att.completed_at.strftime("%a")
            if day_str in chart_dict:
                chart_dict[day_str] += ((att.time_spent_seconds or 0) / 3600.0)
                
        weekly_chart = [ChartDataPoint(day=k, hours=round(v, 1)) for k, v in chart_dict.items()]

        # 5. Quiz Performance (Real accuracy over last 7 days)
        perf_dict = {}
        for att in recent_attempts:
            date_str = att.completed_at.strftime("%b %d")
            if date_str not in perf_dict:
                perf_dict[date_str] = []
            perf_dict[date_str].append(att.score)
            
        quiz_perf_data = []
        for date_str, scores in perf_dict.items():
            avg_acc = sum(scores) / len(scores)
            quiz_perf_data.append(QuizPerformancePoint(date=date_str, score=float(avg_acc), accuracy=float(avg_acc)))
            
        # 6. Recent Activity (Mix of Real Events)
        recent_activity = []
        recent_docs = self.db.query(Document).filter(Document.owner_id == current_user.id).order_by(desc(Document.created_at)).limit(3).all()
        for doc in recent_docs:
            diff = datetime.utcnow() - doc.created_at
            if diff.days > 0: time_str = f"{diff.days}d ago"
            elif diff.seconds // 3600 > 0: time_str = f"{diff.seconds // 3600}h ago"
            elif diff.seconds // 60 > 0: time_str = f"{diff.seconds // 60}m ago"
            else: time_str = "Just now"
            recent_activity.append(RecentActivityItem(action="Uploaded Document", subject=doc.filename, detail="Processed and ready", time=time_str))
            
        recent_notes = self.db.query(Note).filter(Note.owner_id == current_user.id).order_by(desc(Note.created_at)).limit(3).all()
        for note in recent_notes:
            diff = datetime.utcnow() - note.created_at
            if diff.days > 0: time_str = f"{diff.days}d ago"
            elif diff.seconds // 3600 > 0: time_str = f"{diff.seconds // 3600}h ago"
            elif diff.seconds // 60 > 0: time_str = f"{diff.seconds // 60}m ago"
            else: time_str = "Just now"
            recent_activity.append(RecentActivityItem(action="Generated Note", subject=note.title, detail="Note generation completed", time=time_str))

        # Sort combined activities by approximate time
        # This is a bit rough, but sufficient for visual timeline
        recent_activity = recent_activity[:5] 

        # 7. Continue Learning (Recent Docs)
        continue_learning = []
        for doc in recent_docs[:3]:
            continue_learning.append(
                ContinueLearningItem(title=doc.filename, type="Document", time="Recently uploaded")
            )

        # 8. Today's Study Plan Quizzes
        db_quizzes = self.repo.get_daily_quizzes(current_user.id, limit=3)
        study_plan_quizzes = []
        for quiz in db_quizzes:
            total_q = len(quiz.questions) if hasattr(quiz, 'questions') and quiz.questions else 5
            study_plan_quizzes.append(
                StudyPlanQuizItem(
                    id=str(quiz.id),
                    topic=quiz.topic or "General Knowledge",
                    difficulty=quiz.difficulty.capitalize(),
                    status=quiz.status,
                    total_questions=total_q
                )
            )

        # 9. Weekly Study Goal
        target_hours = 10.0
        current_hours = sum(v for v in chart_dict.values())
        weekly_goal = WeeklyStudyGoal(
            current_hours=round(current_hours, 1),
            target_hours=round(target_hours, 1)
        )

        return DashboardResponse(
            username=current_user.full_name or "Student",
            greeting=self.get_greeting(),
            stats=stats,
            badges=profile.badges_earned,
            recentActivity=recent_activity,
            weeklyChartData=weekly_chart,
            subjectProgress=subject_progress,
            continueLearning=continue_learning,
            recommendations=recommendations,
            studyPlanQuizzes=study_plan_quizzes,
            weeklyGoal=weekly_goal,
            quizPerformanceData=quiz_perf_data
        )
