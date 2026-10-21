from sqlalchemy.orm import Session
from uuid import UUID
from app.models.document import Document

class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, owner_id: int, filename: str, file_path: str, file_size: int, content_type: str) -> Document:
        """Saves a new document record in the database."""
        db_doc = Document(
            owner_id=owner_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            content_type=content_type
        )
        self.session.add(db_doc)
        self.session.commit()
        self.session.refresh(db_doc)
        return db_doc

    def get_by_owner_id(self, owner_id: int) -> list[Document]:
        return self.session.query(Document).filter(Document.owner_id == owner_id).all()
