from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID
from app.models.study_note import StudyNote

class StudyNoteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document_id: UUID, owner_id: UUID, note_type: str, content: str) -> StudyNote:
        db_note = StudyNote(
            document_id=document_id,
            owner_id=owner_id,
            note_type=note_type,
            content=content
        )
        self.session.add(db_note)
        await self.session.commit()
        await self.session.refresh(db_note)
        return db_note

    async def get_by_document(self, document_id: UUID, owner_id: UUID) -> List[StudyNote]:
        result = await self.session.execute(
            select(StudyNote)
            .where(StudyNote.document_id == document_id, StudyNote.owner_id == owner_id)
            .order_by(StudyNote.created_at.desc())
        )
        return result.scalars().all()
        
    async def get_by_id(self, note_id: UUID, owner_id: UUID) -> Optional[StudyNote]:
        result = await self.session.execute(
            select(StudyNote).where(StudyNote.id == note_id, StudyNote.owner_id == owner_id)
        )
        return result.scalars().first()
