from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import HTTPException
from uuid import UUID
from typing import Optional
from google import genai
import json
from app.models.document import Document
from app.models.processed_chunk import ProcessedChunk
from app.repositories.quiz import QuizRepository
from app.DTOs.quiz import QuizGeneration, DifficultyEnum
from app.config.config import settings
from datetime import date
from sqlalchemy import desc
from app.models.srs_flashcard import SRSDeck, SRSCard, ReviewHistory

class QuizGenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.quiz_repo = QuizRepository(db)

    async def generate_and_save_quiz(self, document_id: Optional[UUID], owner_id: int, difficulty: DifficultyEnum, num_questions: int = 10, source_text: Optional[str] = None, topic: Optional[str] = None):
        if not settings.GEMINI_API_KEY:
            raise HTTPException(status_code=400, detail="Gemini API Key is missing. Please configure a real key in .env.")
            
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
        full_text = ""
        
        if source_text:
            full_text = source_text
        elif document_id:
            # 1. Verify document
            doc_result = self.db.execute(select(Document).where(Document.id == document_id, Document.owner_id == owner_id))
            doc = doc_result.scalars().first()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")
            if doc.upload_status != "completed":
                raise HTTPException(status_code=400, detail="Document has not been processed yet")
    
            # 2. Gather Document Context
            chunk_result = self.db.execute(
                select(ProcessedChunk)
                .where(ProcessedChunk.document_id == document_id)
                .order_by(ProcessedChunk.page_number, ProcessedChunk.chunk_index)
            )
            chunks = chunk_result.scalars().all()
            
            if not chunks:
                raise HTTPException(status_code=400, detail="The selected document contains no readable text.")
    
            full_text = "\n\n".join([chunk.text_content for chunk in chunks])
            if not full_text.strip():
                raise HTTPException(status_code=400, detail="The selected document contains no readable text.")
                
            if len(full_text) > 400000:
                full_text = full_text[:400000] + "\n\n[DOCUMENT TRUNCATED DUE TO LENGTH LIMITS]"
        else:
            if not topic:
                raise HTTPException(status_code=400, detail="Must provide either a document, source text, or topic.")
            full_text = f"General knowledge regarding the topic: {topic}"
        
        system_prompt = f"You are an expert test creator. Create exactly {num_questions} quiz questions based on the provided document text. The difficulty level must be strictly: {difficulty.value.upper()}. You MUST generate a diverse mix of question types: mcq, short, long, coding, and case_study. For mcq, provide exactly 4 options. Ensure the correct_answer matches the options, and provide a clear explanation."
        
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=f"System: {system_prompt}\n\nUser: Document Text:\n{full_text}",
                config={"response_mime_type": "application/json", "response_schema": QuizGeneration}
            )
            response_obj = QuizGeneration(**json.loads(response.text))
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                raise HTTPException(status_code=429, detail="Gemini API rate limit exceeded (Free Tier). Please wait about 1 minute and try again.")
            raise HTTPException(status_code=500, detail=f"Gemini API Error: {error_str}")
        if not response_obj or not response_obj.questions:
            raise HTTPException(status_code=500, detail="Failed to generate quiz questions")

        # 4. Save to Database
        saved_quiz = self.quiz_repo.create_quiz(
            document_id=document_id,
            owner_id=owner_id,
            difficulty=difficulty.value,
            generated_questions=response_obj.questions,
            topic=topic
        )
        
        return saved_quiz

    async def generate_daily_quizzes(self, owner_id: int):
        today = date.today()
        existing_quizzes = self.quiz_repo.get_daily_quizzes(owner_id, today)
        if existing_quizzes:
            return existing_quizzes

        # Find weak topics from SRS
        weak_topics = []
        try:
            # Query decks where average easiness factor of cards is low or there are high wrong answers
            # Keep it simple: just fetch 3 distinct topics from the user's decks
            deck_result = self.db.execute(
                select(SRSDeck.topic, SRSDeck.document_id)
                .where(SRSDeck.owner_id == owner_id, SRSDeck.topic != None)
                .distinct()
                .limit(3)
            )
            weak_topics = deck_result.all()
        except Exception as e:
            print("Error fetching weak topics:", e)

        # Fallback to general documents if not enough topics
        if len(weak_topics) < 3:
            doc_result = self.db.execute(
                select(Document.id)
                .where(Document.owner_id == owner_id, Document.upload_status == "completed")
                .limit(3 - len(weak_topics))
            )
            for d in doc_result.scalars().all():
                weak_topics.append((None, d))

        if not weak_topics:
            # Fallback topics if user has nothing
            weak_topics = [("General Science", None), ("Mathematics", None), ("History", None)]

        quizzes = []
        difficulties = [DifficultyEnum.easy, DifficultyEnum.medium, DifficultyEnum.hard]
        
        # We need exactly 3 topics. If we have less, repeat them to reach 3.
        while len(weak_topics) < 3:
            weak_topics.append(weak_topics[0])
            
        generation_errors = []
        for i, (topic, doc_id) in enumerate(weak_topics[:3]):
            try:
                if doc_id:
                    quiz = await self.generate_and_save_quiz(
                        document_id=doc_id,
                        owner_id=owner_id,
                        difficulty=difficulties[i],
                        num_questions=5,
                        topic=topic
                    )
                else:
                    quiz = await self.generate_and_save_quiz(
                        document_id=None,
                        owner_id=owner_id,
                        difficulty=difficulties[i],
                        num_questions=5,
                        topic=topic or f"Topic {i+1}"
                    )
                
                # Update daily properties
                quiz.is_daily = True
                quiz.quiz_date = today
                quiz.quiz_number = i + 1
                self.db.commit()
                quizzes.append(quiz)
            except Exception as e:
                print(f"Error generating daily quiz {i+1}:", e)
                generation_errors.append(f"Quiz {i+1} failed: {str(e)}")
                
        if not quizzes:
             raise HTTPException(status_code=500, detail=f"Failed to generate any daily quizzes. Reasons: {', '.join(generation_errors)}")
             
        return quizzes
