import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.config.config import settings
from app.repositories.document import DocumentRepository
from app.DTOs.document import DocumentResponse
from app.services.kg_service import KnowledgeGraphService

class DocumentService:
    def __init__(self, db: Session):
        self.doc_repo = DocumentRepository(db)
        self.doc_repo.session = db # Fix for repo using session instead of db
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    def validate_file(self, file: UploadFile) -> None:
        """Validates file type and size."""
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file.content_type}' is not allowed. Allowed types are PDF, DOCX, and PPTX."
            )
        
        # We will check the file size while reading it in chunks.
        # Alternatively, if headers provide content-length, we can check early (though it can be spoofed).
        if file.size and file.size > settings.MAX_UPLOAD_SIZE:
             raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB limit."
            )

    async def save_file_to_disk(self, file: UploadFile) -> tuple[str, int]:
        """Saves the uploaded file to disk securely in chunks and returns the path and size."""
        # Secure filename generation to prevent directory traversal attacks
        ext = os.path.splitext(file.filename)[1]
        secure_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, secure_filename)
        
        file_size = 0
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                while content := await file.read(1024 * 1024):  # Read in 1MB chunks
                    file_size += len(content)
                    if file_size > settings.MAX_UPLOAD_SIZE:
                        # Clean up if file exceeds limit during stream
                        os.remove(file_path)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File size exceeds the {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB limit."
                        )
                    await out_file.write(content)
        except Exception as e:
            # Clean up on generic failure
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail="Failed to save file securely.")
            
        return file_path, file_size

    async def upload_document(self, file: UploadFile, owner_id: int) -> DocumentResponse:
        """Orchestrates file validation, saving to disk, and database insertion."""
        self.validate_file(file)
        
        file_path, file_size = await self.save_file_to_disk(file)
        
        new_doc = self.doc_repo.create(
            owner_id=owner_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            content_type=file.content_type
        )
        
        # Trigger Knowledge Graph Extraction
        kg_service = KnowledgeGraphService(self.doc_repo.session)
        kg_service.extract_topics_from_document(owner_id, new_doc.id, new_doc.filename)
        
        return DocumentResponse.model_validate(new_doc)

    def get_documents(self, user_id: int):
        from app.models.document import Document
        return self.doc_repo.session.query(Document).filter(Document.owner_id == user_id).order_by(Document.created_at.desc()).all()

    def rename_document(self, user_id: int, document_id: UUID, new_name: str):
        from app.models.document import Document
        doc = self.doc_repo.session.query(Document).filter(Document.id == document_id, Document.owner_id == user_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc.filename = new_name
        self.doc_repo.session.commit()
        self.doc_repo.session.refresh(doc)
        return doc

    def delete_document(self, user_id: int, document_id: UUID):
        from app.models.document import Document
        doc = self.doc_repo.session.query(Document).filter(Document.id == document_id, Document.owner_id == user_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from disk
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except:
                pass
                
        self.doc_repo.session.delete(doc)
        self.doc_repo.session.commit()

    def download_document(self, user_id: int, document_id: UUID):
        from app.models.document import Document
        doc = self.doc_repo.session.query(Document).filter(Document.id == document_id, Document.owner_id == user_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not os.path.exists(doc.file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
            
        return doc
