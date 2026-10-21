from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.models.workspace import Workspace, RecentFile, PinnedDocument, RecentActivity
from app.models.document import Document
from app.models.tutor import TutorSession
from sqlalchemy import desc

class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_workspace(self, owner_id: int) -> Workspace:
        workspace = self.db.query(Workspace).filter(Workspace.owner_id == owner_id).first()
        if not workspace:
            workspace = Workspace(owner_id=owner_id)
            self.db.add(workspace)
            self.db.commit()
            self.db.refresh(workspace)
        return workspace

    def get_dashboard_data(self, owner_id: int):
        workspace = self.get_or_create_workspace(owner_id)
        
        # Recent uploads (Documents)
        recent_docs = self.db.query(Document).filter(Document.owner_id == owner_id).order_by(desc(Document.created_at)).limit(5).all()
        recent_uploads = [
            {
                "id": doc.id,
                "filename": doc.filename,
                "content_type": doc.content_type,
                "file_size": doc.file_size,
                "last_opened_at": doc.created_at
            }
            for doc in recent_docs
        ]
        
        # Pinned documents
        pinned = self.db.query(PinnedDocument, Document).join(Document, PinnedDocument.document_id == Document.id).filter(PinnedDocument.workspace_id == workspace.id).order_by(desc(PinnedDocument.pinned_at)).limit(5).all()
        pinned_files = [
            {
                "id": p.id,
                "document_id": p.document_id,
                "filename": doc.filename,
                "pinned_at": p.pinned_at
            }
            for p, doc in pinned
        ]
        
        # Last opened document
        last_opened = self.db.query(RecentFile, Document).join(Document, RecentFile.document_id == Document.id).filter(RecentFile.workspace_id == workspace.id).order_by(desc(RecentFile.last_opened_at)).first()
        
        last_opened_doc = None
        if last_opened:
            last_opened_doc = {
                "id": last_opened[1].id,
                "filename": last_opened[1].filename,
                "content_type": last_opened[1].content_type,
                "file_size": last_opened[1].file_size,
                "last_opened_at": last_opened[0].last_opened_at
            }
        elif recent_uploads:
            # Fallback to most recent upload
            last_opened_doc = recent_uploads[0]

        # Recent chats
        chats = self.db.query(TutorSession).filter(TutorSession.owner_id == owner_id).order_by(desc(TutorSession.updated_at)).limit(5).all()
        recent_chats = [
            {
                "id": chat.id,
                "title": chat.title,
                "updated_at": chat.updated_at
            }
            for chat in chats
        ]
        
        # Activities
        activities_data = self.db.query(RecentActivity).filter(RecentActivity.workspace_id == workspace.id).order_by(desc(RecentActivity.created_at)).limit(10).all()
        
        return {
            "recent_uploads": recent_uploads,
            "pinned_files": pinned_files,
            "last_opened_document": last_opened_doc,
            "recent_chats": recent_chats,
            "activities": activities_data
        }
