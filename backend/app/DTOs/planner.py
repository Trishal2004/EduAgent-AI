from pydantic import BaseModel
from typing import List, Any
from datetime import datetime

class PlannerGenerateRequest(BaseModel):
    exam_date: str
    subjects: str
    study_time: int

class PlannerResponse(BaseModel):
    id: int
    target_exam_date: datetime
    subjects: str
    daily_hours: int
    plan_data: List[Any]
    created_at: datetime

    class Config:
        from_attributes = True
