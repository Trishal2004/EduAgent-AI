from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
import json
from app.models.mentor import MentorStudyPlan, Recommendation, WeakTopic, Goal, MentorChat
from app.models.analytics import Performance
from app.DTOs.mentor import MentorDashboardResponse, ChatMessageRequest, MentorChatResponse
from app.config.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import List

class MentorInsightsGeneration(BaseModel):
    weak_topics: List[str] = Field(description="List of weak topics identified from the user's performance.")
    recommendations: List[str] = Field(description="Actionable recommendations to improve performance.")
    daily_plan: List[str] = Field(description="A list of 2-3 tasks for today's study plan.")
    weekly_plan: List[str] = Field(description="A list of 3-5 tasks for the week's study plan.")

class MentorService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = ChatOpenAI(temperature=0.7, api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")

    def get_dashboard(self, owner_id: int):
        active_goals = self.db.query(Goal).filter(Goal.owner_id == owner_id, Goal.status == "active").order_by(Goal.target_date).all()
        weak_topics = self.db.query(WeakTopic).filter(WeakTopic.owner_id == owner_id).order_by(WeakTopic.score_indicator).all()
        recommendations = self.db.query(Recommendation).filter(Recommendation.owner_id == owner_id).order_by(Recommendation.priority.desc()).limit(5).all()
        
        today_plan = self.db.query(MentorStudyPlan).filter(MentorStudyPlan.owner_id == owner_id, MentorStudyPlan.plan_type == "daily").order_by(desc(MentorStudyPlan.created_at)).first()
        weekly_plan = self.db.query(MentorStudyPlan).filter(MentorStudyPlan.owner_id == owner_id, MentorStudyPlan.plan_type == "weekly").order_by(desc(MentorStudyPlan.created_at)).first()
        
        return {
            "active_goals": active_goals,
            "weak_topics": weak_topics,
            "recommendations": recommendations,
            "today_plan": today_plan,
            "weekly_plan": weekly_plan
        }

    def generate_insights(self, owner_id: int):
        # 1. Gather context from Performance table
        performances = self.db.query(Performance).filter(Performance.user_id == owner_id).all()
        perf_context = "User has no performance data yet."
        if performances:
            perf_context = "\n".join([f"Subject: {p.subject}, Strong Score: {p.strong_score}, Weak Score: {p.weak_score}" for p in performances])

        # 2. Call LLM for structured insights
        structured_llm = self.llm.with_structured_output(MentorInsightsGeneration)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert AI Academic Mentor. Analyze the user's performance data and generate a personalized study strategy."),
            ("user", f"Performance Data:\n{perf_context}")
        ])
        
        response: MentorInsightsGeneration = prompt | structured_llm
        result = response.invoke({})

        # 3. Save to database
        self.db.query(MentorStudyPlan).filter(MentorStudyPlan.owner_id == owner_id).delete()
        self.db.query(Goal).filter(Goal.owner_id == owner_id).delete()
        self.db.query(WeakTopic).filter(WeakTopic.owner_id == owner_id).delete()
        self.db.query(Recommendation).filter(Recommendation.owner_id == owner_id).delete()
        
        # Goal (Mock a target date)
        new_goal = Goal(owner_id=owner_id, goal_text="Improve on weak areas", target_date=datetime.utcnow() + timedelta(days=7))
        self.db.add(new_goal)
        
        # Weak Topics
        for wt in result.weak_topics:
            self.db.add(WeakTopic(owner_id=owner_id, topic_name=wt, score_indicator=50.0))
            
        # Recommendations
        for idx, rec in enumerate(result.recommendations):
            self.db.add(Recommendation(owner_id=owner_id, topic="General", action_type="review", description=rec, priority=10-idx))
            
        # Study Plans
        daily = MentorStudyPlan(owner_id=owner_id, plan_type="daily", content={"tasks": result.daily_plan})
        weekly = MentorStudyPlan(owner_id=owner_id, plan_type="weekly", content={"tasks": result.weekly_plan})
        self.db.add_all([daily, weekly])
        
        self.db.commit()
        return self.get_dashboard(owner_id)

    def process_chat(self, owner_id: int, request: ChatMessageRequest):
        # Save user message
        user_msg = MentorChat(owner_id=owner_id, role="user", content=request.message)
        self.db.add(user_msg)
        self.db.flush()
        
        # Get chat history for context
        history = self.db.query(MentorChat).filter(MentorChat.owner_id == owner_id).order_by(MentorChat.created_at.desc()).limit(10).all()
        history.reverse()

        mentor_prompt = """You are the dedicated Academic Mentor for "EduAgent AI"—an intelligent, grounded, and supportive learning assistant designed for computer science and engineering students.

Your Core Directives:
1. Pedagogical Approach:
   - Act as an encouraging, peer-level technical mentor.
   - Use the Socratic method when students ask conceptual questions: guide them step-by-step with intuitive analogies before providing raw definitions.
   - For algorithmic and mathematical topics (e.g., Page Replacement, Fuzzy Sets, Database Normalization), break down the problem into sequential steps and include concrete trace tables.

2. Tone & Style:
   - Clear, concise, and structured.
   - Use Markdown formatting generously: bold key terms, use bullet points, and structure multi-step solutions clearly.
   - Avoid long walls of unbroken text.
   - Validate effort and maintain a constructive, encouraging tone without patronizing.

3. Code & Technical Precision:
   - Provide syntactically valid, production-grade Python, SQL, or JavaScript code blocks with inline comments explaining critical logic.
   - When debugging student code, always explain why an error occurred before providing the corrected snippet."""

        messages = [SystemMessage(content=mentor_prompt)]
        for h in history:
            if h.role == "user":
                messages.append(HumanMessage(content=h.content))
            else:
                messages.append(AIMessage(content=h.content))
        
        # Call LLM
        response = self.llm.invoke(messages)
        ai_reply = response.content
        
        ai_msg = MentorChat(owner_id=owner_id, role="ai", content=ai_reply)
        self.db.add(ai_msg)
        self.db.commit()
        self.db.refresh(ai_msg)
        
        return ai_msg

    def get_chat_history(self, owner_id: int):
        return self.db.query(MentorChat).filter(MentorChat.owner_id == owner_id).order_by(MentorChat.created_at).all()
