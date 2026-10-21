import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.study_plan import StudyPlan
from app.DTOs.planner import PlannerGenerateRequest, PlannerResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config.config import settings

class PlannerService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = ChatOpenAI(temperature=0.3, api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")

    async def generate_plan(self, user_id: int, request: PlannerGenerateRequest) -> PlannerResponse:
        try:
            exam_date = datetime.strptime(request.exam_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert academic planner. Based on the target exam date, subjects to cover, and available daily study time, generate a structured study schedule spanning the next 5-7 days (or until the exam if it's sooner). Output a raw JSON array of objects with these keys: 'day' (e.g. 'Monday' or date), 'topics' (array of strings), 'type' (e.g. 'Deep Dive', 'Practice', 'Assessment'), and 'time' (e.g. '4 hrs'). Do not use markdown backticks, just raw JSON."),
            ("user", f"Target Exam Date: {request.exam_date}\nSubjects: {request.subjects}\nDaily Hours: {request.study_time}")
        ])

        chain = prompt | self.llm
        response = await chain.ainvoke({})

        try:
            plan_data = json.loads(response.content.strip())
        except json.JSONDecodeError:
            plan_data = [{"day": "Today", "topics": ["Review fundamentals"], "type": "Deep Dive", "time": f"{request.study_time} hrs"}]

        plan = StudyPlan(
            user_id=user_id,
            target_exam_date=exam_date,
            subjects=request.subjects,
            daily_hours=request.study_time,
            plan_data=plan_data
        )

        # Delete old plan
        self.db.query(StudyPlan).filter(StudyPlan.user_id == user_id).delete()
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        return PlannerResponse.model_validate(plan)

    def get_plan(self, user_id: int) -> Optional[PlannerResponse]:
        plan = self.db.query(StudyPlan).filter(StudyPlan.user_id == user_id).order_by(StudyPlan.created_at.desc()).first()
        if not plan:
            return None
        return PlannerResponse.model_validate(plan)
