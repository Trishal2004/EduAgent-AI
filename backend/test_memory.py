import asyncio
from app.db.session import SessionLocal
from app.services.tutor_service import TutorService
from app.DTOs.tutor import ChatRequest

async def main():
    db = SessionLocal()
    from app.models.user import User
    user = db.query(User).first()
    
    service = TutorService(db)
    
    # Message 1
    print("Sending message 1...")
    req1 = ChatRequest(question="What is DBMS?")
    res1 = await service.chat(req1, user.id)
    session_id = res1.session_id
    print(f"Session created: {session_id}")
    print(f"AI: {res1.ai_message.content[:50]}...")
    
    # Message 2
    print("Sending message 2...")
    req2 = ChatRequest(session_id=session_id, question="What are its advantages?")
    res2 = await service.chat(req2, user.id)
    print(f"AI: {res2.ai_message.content[:50]}...")

asyncio.run(main())
