from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LessonBase(BaseModel):
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    order: int

class LessonResponse(LessonBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None

class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True

class ProgressResponse(BaseModel):
    id: int
    lesson_id: int
    status: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    course: CourseResponse
    progress: List[ProgressResponse] = []

    class Config:
        from_attributes = True

class ProgressUpdateRequest(BaseModel):
    lesson_id: int
    status: str # not_started, in_progress, completed
