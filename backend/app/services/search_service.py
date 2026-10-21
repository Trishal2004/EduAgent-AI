from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.note import Note
from app.models.srs_flashcard import SRSDeck
from app.models.course import Course
from app.models.quiz import Quiz
from app.models.tutor import ChatMessage, TutorSession
from app.DTOs.search import SearchResultItem, GlobalSearchResponse

class GlobalSearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_all(self, user_id: int, query: str) -> GlobalSearchResponse:
        results = []
        pattern = f"%{query}%"

        # 1. Documents
        docs = self.db.query(Document).filter(
            Document.owner_id == user_id,
            Document.filename.ilike(pattern)
        ).limit(5).all()
        for d in docs:
            results.append(SearchResultItem(
                id=str(d.id), type="document", title=d.filename,
                snippet=f"File size: {round(d.file_size/1024)} KB", url="/documents"
            ))

        # 2. Notes
        notes = self.db.query(Note).filter(
            Note.owner_id == user_id,
            (Note.title.ilike(pattern)) | (Note.content.ilike(pattern))
        ).limit(5).all()
        for n in notes:
            results.append(SearchResultItem(
                id=str(n.id), type="note", title=n.title,
                snippet=n.content[:100] if n.content else "", url="/notes"
            ))

        # 3. Flashcards Decks
        decks = self.db.query(SRSDeck).filter(
            SRSDeck.owner_id == user_id,
            SRSDeck.title.ilike(pattern)
        ).limit(5).all()
        for d in decks:
            results.append(SearchResultItem(
                id=str(d.id), type="flashcard", title=d.title,
                snippet=d.description or "Flashcard Deck", url="/flashcards"
            ))

        # 4. Courses
        courses = self.db.query(Course).filter(
            Course.owner_id == user_id,
            Course.title.ilike(pattern)
        ).limit(5).all()
        for c in courses:
            results.append(SearchResultItem(
                id=str(c.id), type="course", title=c.title,
                snippet=c.description or "Course", url="/courses"
            ))

        # 5. Quizzes
        quizzes = self.db.query(Quiz).filter(
            Quiz.owner_id == user_id,
            Quiz.title.ilike(pattern)
        ).limit(5).all()
        for q in quizzes:
            results.append(SearchResultItem(
                id=str(q.id), type="quiz", title=q.title,
                snippet=f"Quiz - {q.total_questions} Questions", url="/quiz"
            ))

        # 6. AI Chats
        chats = self.db.query(ChatMessage).join(TutorSession).filter(
            TutorSession.owner_id == user_id,
            ChatMessage.content.ilike(pattern)
        ).limit(5).all()
        for ch in chats:
            results.append(SearchResultItem(
                id=str(ch.id), type="chat", title="AI Tutor Conversation",
                snippet=ch.content[:100] if ch.content else "", url="/tutor"
            ))

        return GlobalSearchResponse(
            query=query,
            total_results=len(results),
            results=results
        )
