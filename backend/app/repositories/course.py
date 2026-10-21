from sqlalchemy.orm import Session
from app.models.course import Course, Lesson, Enrollment, Progress
from typing import List, Optional

class CourseRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_courses(self) -> List[Course]:
        return self.session.query(Course).all()

    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        return self.session.query(Course).filter(Course.id == course_id).first()

    def get_enrollments(self, user_id: int) -> List[Enrollment]:
        return self.session.query(Enrollment).filter(Enrollment.user_id == user_id).all()

    def get_enrollment(self, user_id: int, course_id: int) -> Optional[Enrollment]:
        return self.session.query(Enrollment).filter(
            Enrollment.user_id == user_id, 
            Enrollment.course_id == course_id
        ).first()

    def enroll(self, user_id: int, course_id: int) -> Enrollment:
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        
        # Initialize progress for all lessons in this course
        course = self.get_course_by_id(course_id)
        if course:
            for lesson in course.lessons:
                prog = Progress(enrollment_id=enrollment.id, lesson_id=lesson.id, status="not_started")
                self.session.add(prog)
            self.session.commit()
            
        return enrollment

    def unenroll(self, user_id: int, course_id: int) -> bool:
        enrollment = self.get_enrollment(user_id, course_id)
        if enrollment:
            self.session.delete(enrollment)
            self.session.commit()
            return True
        return False

    def update_progress(self, user_id: int, course_id: int, lesson_id: int, status: str) -> Optional[Progress]:
        enrollment = self.get_enrollment(user_id, course_id)
        if not enrollment:
            return None
            
        progress = self.session.query(Progress).filter(
            Progress.enrollment_id == enrollment.id,
            Progress.lesson_id == lesson_id
        ).first()
        
        if progress:
            progress.status = status
            self.session.commit()
            self.session.refresh(progress)
            
        return progress
