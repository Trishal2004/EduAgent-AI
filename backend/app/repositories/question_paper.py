from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID
from app.models.question_paper import QuestionPaper

class QuestionPaperRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document_id: UUID, owner_id: UUID, paper_type: str, content_json: dict, pdf_file_path: str) -> QuestionPaper:
        paper = QuestionPaper(
            document_id=document_id,
            owner_id=owner_id,
            paper_type=paper_type,
            content_json=content_json,
            pdf_file_path=pdf_file_path
        )
        self.session.add(paper)
        await self.session.commit()
        await self.session.refresh(paper)
        return paper

    async def get_by_document(self, document_id: UUID, owner_id: UUID) -> List[QuestionPaper]:
        result = await self.session.execute(
            select(QuestionPaper)
            .where(QuestionPaper.document_id == document_id, QuestionPaper.owner_id == owner_id)
            .order_by(QuestionPaper.created_at.desc())
        )
        return result.scalars().all()
        
    async def get_by_id(self, paper_id: UUID, owner_id: UUID) -> Optional[QuestionPaper]:
        result = await self.session.execute(
            select(QuestionPaper)
            .where(QuestionPaper.id == paper_id, QuestionPaper.owner_id == owner_id)
        )
        return result.scalars().first()
