import sys
import os
import asyncio
sys.path.append("/Users/k.trishal/Desktop/EduAgent AI/backend")

from app.db.session import SessionLocal
from app.services.dashboard_service import DashboardService
from app.models.user import User
from app.models.analytics import Analytics, QuizResult, StudySession, Performance
from app.models.workspace import RecentActivity, RecentFile

def run_test():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No user found")
            return
        
        service = DashboardService(db)
        try:
            response = service.generate_dashboard(user)
            print("Successfully generated dashboard")
            print("Response:", response.model_dump_json(indent=2))
        except Exception as e:
            print("Error generating dashboard:")
            import traceback
            traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
