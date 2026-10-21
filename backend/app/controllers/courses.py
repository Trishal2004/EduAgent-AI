from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.security import deps
from app.models.user import User
from app.DTOs.course import CourseResponse, EnrollmentResponse, ProgressResponse, ProgressUpdateRequest
from app.services.course_service import CourseService
from typing import List

router = APIRouter()

@router.get("/", response_model=List[CourseResponse])
def get_all_courses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = CourseService(db)
    return service.get_available_courses()

@router.get("/my", response_model=List[EnrollmentResponse])
def get_my_courses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = CourseService(db)
    return service.get_my_courses(current_user.id)

@router.post("/enroll", response_model=EnrollmentResponse)
def enroll_course(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = CourseService(db)
    return service.enroll(current_user.id, course_id)

@router.get("/{course_id}", response_model=CourseResponse)
def get_course_details(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = CourseService(db)
    return service.get_course_details(course_id)

@router.put("/progress", response_model=ProgressResponse)
def update_progress(
    course_id: int,
    request: ProgressUpdateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = CourseService(db)
    return service.update_progress(current_user.id, course_id, request.lesson_id, request.status)

@router.delete("/{course_id}")
def unenroll_course(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = CourseService(db)
    return service.unenroll(current_user.id, course_id)
