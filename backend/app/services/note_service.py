from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.note import Note, Folder, Tag
from app.DTOs.note import NoteCreate, NoteUpdate, FolderBase, TagBase
from typing import List, Optional

class NoteService:
    def __init__(self, db: Session):
        self.db = db

    # Folders
    def get_folders(self, user_id: int):
        return self.db.query(Folder).filter(Folder.owner_id == user_id).all()

    def create_folder(self, user_id: int, folder_in: FolderBase):
        folder = Folder(owner_id=user_id, name=folder_in.name)
        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)
        return folder

    def delete_folder(self, user_id: int, folder_id: int):
        folder = self.db.query(Folder).filter(Folder.owner_id == user_id, Folder.id == folder_id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        self.db.delete(folder)
        self.db.commit()

    # Tags
    def get_tags(self, user_id: int):
        return self.db.query(Tag).filter(Tag.owner_id == user_id).all()

    def create_tag(self, user_id: int, tag_in: TagBase):
        tag = Tag(owner_id=user_id, name=tag_in.name)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete_tag(self, user_id: int, tag_id: int):
        tag = self.db.query(Tag).filter(Tag.owner_id == user_id, Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        self.db.delete(tag)
        self.db.commit()

    # Notes
    def create_note(self, user_id: int, note_in: NoteCreate):
        note = Note(
            owner_id=user_id,
            folder_id=note_in.folder_id,
            document_id=note_in.document_id,
            title=note_in.title,
            note_type=note_in.note_type,
            content=note_in.content
        )
        
        if note_in.tags:
            tags = self.db.query(Tag).filter(Tag.id.in_(note_in.tags), Tag.owner_id == user_id).all()
            note.tags = tags
            
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def get_notes(
        self, user_id: int, folder_id: Optional[int] = None, 
        tag_id: Optional[int] = None, is_favorite: Optional[bool] = None, 
        search: Optional[str] = None
    ):
        query = self.db.query(Note).filter(Note.owner_id == user_id)
        
        if folder_id is not None:
            query = query.filter(Note.folder_id == folder_id)
            
        if is_favorite is not None:
            query = query.filter(Note.is_favorite == is_favorite)
            
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Note.title.ilike(search_pattern))
            
        if tag_id is not None:
            query = query.filter(Note.tags.any(id=tag_id))
            
        return query.order_by(Note.created_at.desc()).all()

    def get_note(self, user_id: int, note_id: int):
        note = self.db.query(Note).filter(Note.owner_id == user_id, Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note

    def update_note(self, user_id: int, note_id: int, note_in: NoteUpdate):
        note = self.get_note(user_id, note_id)
        
        update_data = note_in.dict(exclude_unset=True)
            
        if 'tags' in update_data:
            tag_ids = update_data.pop('tags')
            tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids), Tag.owner_id == user_id).all()
            note.tags = tags
            
        for field, value in update_data.items():
            setattr(note, field, value)
            
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete_note(self, user_id: int, note_id: int):
        note = self.get_note(user_id, note_id)
        self.db.delete(note)
        self.db.commit()

    def toggle_favorite(self, user_id: int, note_id: int):
        note = self.get_note(user_id, note_id)
        note.is_favorite = not note.is_favorite
        self.db.commit()
        self.db.refresh(note)
        return note
