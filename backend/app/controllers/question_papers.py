import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.security import deps
from app.models.user import User
from app.DTOs.question_paper import QuestionPaperResponse, PaperPatternEnum
from app.services.question_paper import QuestionPaperService
from app.repositories.question_paper import QuestionPaperRepository

router = APIRouter()

@router.post("/{document_id}/question-papers", response_model=QuestionPaperResponse)
async def generate_question_paper(
    document_id: UUID,
    pattern: PaperPatternEnum,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generates a formal university-style Question Paper and exports it as a PDF.
    """
    service = QuestionPaperService(db)
    return await service.generate_paper(
        document_id=document_id, 
        owner_id=current_user.id,
        pattern=pattern
    )

@router.get("/{document_id}/question-papers", response_model=List[QuestionPaperResponse])
async def list_document_papers(
    document_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Lists all generated question papers for a specific document."""
    repo = QuestionPaperRepository(db)
    return await repo.get_by_document(document_id, current_user.id)

@router.get("/question-papers/{paper_id}/download")
async def download_question_paper_pdf(
    paper_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Downloads the actual PDF file of the question paper."""
    repo = QuestionPaperRepository(db)
    paper = await repo.get_by_id(paper_id, current_user.id)
    
    if not paper or not paper.pdf_file_path:
        raise HTTPException(status_code=404, detail="Question paper PDF not found")
        
    if not os.path.exists(paper.pdf_file_path):
        raise HTTPException(status_code=404, detail="Physical PDF file missing from disk")
        
    return FileResponse(
        path=paper.pdf_file_path, 
        filename=f"Question_Paper_{paper_id}.pdf",
        media_type="application/pdf"
    )
