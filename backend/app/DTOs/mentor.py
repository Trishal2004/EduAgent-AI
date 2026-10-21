from pydantic import BaseModel
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class StudyPlanResponse(BaseModel):
    id: UUID
    plan_type: str
    content: Any
    created_at: datetime
    
    model_config = {"from_attributes": True}

class RecommendationResponse(BaseModel):
    id: UUID
    topic: str
    action_type: str
    description: str
    priority: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

class WeakTopicResponse(BaseModel):
    id: UUID
    topic_name: str
    score_indicator: Optional[float]
    identified_at: datetime
    
    model_config = {"from_attributes": True}

class GoalResponse(BaseModel):
    id: UUID
    goal_text: str
    target_date: datetime
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

class MentorChatResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

class MentorDashboardResponse(BaseModel):
    active_goals: List[GoalResponse]
    weak_topics: List[WeakTopicResponse]
    recommendations: List[RecommendationResponse]
    today_plan: Optional[StudyPlanResponse]
    weekly_plan: Optional[StudyPlanResponse]
    
    model_config = {"from_attributes": True}

class ChatMessageRequest(BaseModel):
    message: str
