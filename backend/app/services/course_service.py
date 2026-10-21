from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.course import CourseRepository
from app.DTOs.course import CourseResponse, EnrollmentResponse, ProgressResponse
from typing import List

class CourseService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CourseRepository(db)

    def get_available_courses(self) -> List[CourseResponse]:
        courses = self.repo.get_all_courses()
        return [CourseResponse.model_validate(c) for c in courses]

    def get_my_courses(self, user_id: int) -> List[EnrollmentResponse]:
        enrollments = self.repo.get_enrollments(user_id)
        return [EnrollmentResponse.model_validate(e) for e in enrollments]

    def enroll(self, user_id: int, course_id: int) -> EnrollmentResponse:
        course = self.repo.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
            
        existing = self.repo.get_enrollment(user_id, course_id)
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled")
            
        enrollment = self.repo.enroll(user_id, course_id)
        return EnrollmentResponse.model_validate(enrollment)

    def get_course_details(self, course_id: int) -> CourseResponse:
        course = self.repo.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return CourseResponse.model_validate(course)

    def unenroll(self, user_id: int, course_id: int):
        success = self.repo.unenroll(user_id, course_id)
        if not success:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        return {"detail": "Successfully unenrolled"}

    def update_progress(self, user_id: int, course_id: int, lesson_id: int, status: str) -> ProgressResponse:
        progress = self.repo.update_progress(user_id, course_id, lesson_id, status)
        if not progress:
            raise HTTPException(status_code=404, detail="Progress record not found or not enrolled")
        return ProgressResponse.model_validate(progress)
