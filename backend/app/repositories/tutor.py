from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.tutor import TutorSession, ChatMessage
from typing import List, Optional

class TutorRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_sessions(self, user_id: int) -> List[TutorSession]:
        return self.session.query(TutorSession)\
            .filter(TutorSession.owner_id == user_id)\
            .order_by(desc(TutorSession.updated_at))\
            .all()

    def get_session(self, session_id: str, user_id: int) -> Optional[TutorSession]:
        return self.session.query(TutorSession)\
            .filter(TutorSession.id == session_id, TutorSession.owner_id == user_id)\
            .first()

    def create_session(self, user_id: int, title: str, document_id: Optional[str] = None) -> TutorSession:
        db_session = TutorSession(owner_id=user_id, title=title, document_id=document_id)
        self.session.add(db_session)
        self.session.commit()
        self.session.refresh(db_session)
        return db_session

    def delete_session(self, session_id: str, user_id: int) -> bool:
        db_session = self.get_session(session_id, user_id)
        if db_session:
            self.session.delete(db_session)
            self.session.commit()
            return True
        return False

    def delete_all_sessions(self, user_id: int) -> int:
        count = self.session.query(TutorSession).filter(TutorSession.owner_id == user_id).delete()
        self.session.commit()
        return count

    def rename_session(self, session_id: str, user_id: int, new_title: str) -> Optional[TutorSession]:
        db_session = self.get_session(session_id, user_id)
        if db_session:
            db_session.title = new_title
            self.session.commit()
            self.session.refresh(db_session)
        return db_session

    def add_message(self, session_id: str, role: str, content: Optional[str] = None, structured_data: Optional[dict] = None) -> ChatMessage:
        db_msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            structured_data=structured_data
        )
        self.session.add(db_msg)
        self.session.commit()
        self.session.refresh(db_msg)
        
        # Update session updated_at
        db_session = self.session.query(TutorSession).filter(TutorSession.id == session_id).first()
        if db_session:
            db_session.updated_at = db_msg.created_at
            self.session.commit()
            
        return db_msg
