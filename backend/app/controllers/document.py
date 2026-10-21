from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.security import deps
from app.db.session import get_db
from app.DTOs.document import DocumentResponse
from app.services.document import DocumentService
from app.models.user import User

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Upload a document (PDF, DOCX, PPTX).
    The file will be validated for size and type, saved securely to the backend, 
    and its metadata stored in the database.
    """
    doc_service = DocumentService(db)
    return await doc_service.upload_document(file, owner_id=current_user.id)

from uuid import UUID
from app.services.document_processing import DocumentProcessingService
from app.DTOs.document_chunk import ProcessingResponse

@router.post("/{document_id}/process", response_model=ProcessingResponse)
async def process_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Process an uploaded document to extract text and structure.
    Requires the user to own the document.
    """
    processing_service = DocumentProcessingService(db)
    return await processing_service.process_document(document_id, owner_id=current_user.id)

from fastapi.responses import FileResponse
from typing import List
from app.DTOs.document import DocumentRenameRequest

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """List all documents for the current user."""
    doc_service = DocumentService(db)
    return doc_service.get_documents(current_user.id)

@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a document."""
    doc_service = DocumentService(db)
    doc_service.delete_document(current_user.id, document_id)

@router.put("/{document_id}/rename", response_model=DocumentResponse)
def rename_document(
    document_id: UUID,
    request: DocumentRenameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Rename a document."""
    doc_service = DocumentService(db)
    return doc_service.rename_document(current_user.id, document_id, request.new_name)

@router.get("/{document_id}/download")
def download_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Download a document."""
    doc_service = DocumentService(db)
    doc = doc_service.download_document(current_user.id, document_id)
    return FileResponse(path=doc.file_path, filename=doc.filename, media_type=doc.content_type)
