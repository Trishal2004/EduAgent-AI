from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt
from app.DTOs.quiz import GeneratedQuestion

class QuizRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_quiz(self, document_id: Optional[UUID], owner_id: int, difficulty: str, generated_questions: List[GeneratedQuestion], topic: Optional[str] = None, is_daily: bool = False, quiz_date=None, quiz_number: Optional[int] = None, status: str = "Not Started") -> Quiz:
        """Creates a quiz and saves all associated questions in a single transaction."""
        db_quiz = Quiz(
            document_id=document_id,
            owner_id=owner_id,
            difficulty=difficulty,
            topic=topic,
            is_daily=is_daily,
            quiz_date=quiz_date,
            quiz_number=quiz_number,
            status=status
        )
        self.session.add(db_quiz)
        self.session.flush() # Get the quiz.id
        
        db_questions = [
            QuizQuestion(
                quiz_id=db_quiz.id,
                question_type=q.question_type.value,
                question_text=q.question_text,
                options=q.options,
                correct_answer=q.correct_answer,
                explanation=q.explanation
            ) for q in generated_questions
        ]
        
        self.session.add_all(db_questions)
        self.session.commit()
        
        return self.get_quiz_by_id(db_quiz.id, owner_id)

    def get_quiz_by_id(self, quiz_id: UUID, owner_id: int) -> Optional[Quiz]:
        result = self.session.execute(
            select(Quiz)
            .where(Quiz.id == quiz_id, Quiz.owner_id == owner_id)
            .options(selectinload(Quiz.questions))
        )
        return result.scalars().first()

    def get_user_quizzes(self, owner_id: int) -> List[Quiz]:
        result = self.session.execute(
            select(Quiz)
            .where(Quiz.owner_id == owner_id, Quiz.is_daily == False)
            .order_by(Quiz.created_at.desc())
            .options(selectinload(Quiz.questions), selectinload(Quiz.attempts), selectinload(Quiz.document))
        )
        return result.scalars().all()

    def get_daily_quizzes(self, owner_id: int, quiz_date) -> List[Quiz]:
        result = self.session.execute(
            select(Quiz)
            .where(Quiz.owner_id == owner_id, Quiz.is_daily == True, Quiz.quiz_date == quiz_date)
            .order_by(Quiz.quiz_number.asc())
            .options(selectinload(Quiz.questions), selectinload(Quiz.attempts), selectinload(Quiz.document))
        )
        return result.scalars().all()

    def update_quiz_status(self, quiz_id: UUID, owner_id: int, status: str) -> Optional[Quiz]:
        quiz = self.get_quiz_by_id(quiz_id, owner_id)
        if quiz:
            quiz.status = status
            self.session.commit()
            self.session.refresh(quiz)
        return quiz

    def get_user_attempts(self, owner_id: int) -> List[QuizAttempt]:
        result = self.session.execute(
            select(QuizAttempt)
            .where(QuizAttempt.owner_id == owner_id)
            .order_by(QuizAttempt.completed_at.desc())
        )
        return result.scalars().all()

    def create_attempt(self, quiz_id: UUID, owner_id: int, score: float, total_questions: int, user_answers: dict, time_spent_seconds: int = 0) -> QuizAttempt:
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            owner_id=owner_id,
            score=score,
            total_questions=total_questions,
            user_answers=user_answers,
            time_spent_seconds=time_spent_seconds
        )
        self.session.add(attempt)
        self.session.commit()
        self.session.refresh(attempt)
        return attempt
