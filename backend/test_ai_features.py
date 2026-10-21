import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.config import settings
from app.services.flashcards_generation import FlashcardsGenerationService
from app.services.quiz_generation import QuizGenerationService
from app.services.note_service import NoteService
from app.controllers.general_notes import NoteGenerateRequest
from app.DTOs.quiz import DifficultyEnum

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# We know document 9ef28fd944114205a2f4b69ff7cabffd is completed
DOCUMENT_ID = "9ef28fd9-4411-4205-a2f4-b69ff7cabffd"
OWNER_ID = 1 # k70132172@gmail.com

async def test_flashcards():
    print("Testing Flashcards...")
    try:
        service = FlashcardsGenerationService(db)
        import uuid
        deck = await service.generate_and_save_flashcards(
            document_id=uuid.UUID(DOCUMENT_ID),
            owner_id=OWNER_ID,
            num_cards=3
        )
        print(f"SUCCESS! Deck ID: {deck.id}, Cards: {len(deck.cards)}")
    except Exception as e:
        print(f"FAILED Flashcards: {e}")

async def test_quiz():
    print("\nTesting Quiz...")
    try:
        service = QuizGenerationService(db)
        import uuid
        quiz = await service.generate_and_save_quiz(
            document_id=uuid.UUID(DOCUMENT_ID),
            owner_id=OWNER_ID,
            difficulty=DifficultyEnum.easy,
            num_questions=3
        )
        print(f"SUCCESS! Quiz ID: {quiz.id}, Questions: {len(quiz.questions)}")
    except Exception as e:
        print(f"FAILED Quiz: {e}")

# Notes generator is in controller, let's just test that the genai call works by copying logic
async def test_notes():
    print("\nTesting Notes Generation...")
    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="System: Write a 1-sentence note.\n\nUser: Topic: Hello world"
        )
        print("SUCCESS! Notes response received:", response.text)
    except Exception as e:
        print(f"FAILED Notes: {e}")

async def test_ask_ai():
    print("\nTesting Ask AI (Tutor)...")
    try:
        from app.services.agent.graph import agent_app
        initial_state = {
            "messages": [],
            "current_question": "What is this document about?",
            "original_question": "What is this document about?",
            "session_id": "test_session",
            "document_id": DOCUMENT_ID,
            "owner_id": OWNER_ID,
            "context": [],
            "search_query": "",
            "require_retrieval": False,
            "chat_history": []
        }
        final_state = await agent_app.ainvoke(initial_state)
        print("SUCCESS! Tutor graph returned answer:", final_state.get("answer"))
    except Exception as e:
        print(f"FAILED Ask AI: {e}")

async def main():
    await test_flashcards()
    await test_quiz()
    await test_notes()
    await test_ask_ai()

if __name__ == "__main__":
    asyncio.run(main())
