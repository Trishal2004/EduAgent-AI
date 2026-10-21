from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.security import deps
from app.models.user import User
from app.models.note import Note
from app.DTOs.note import NoteCreate, NoteUpdate, NoteResponse, FolderBase, FolderResponse, TagBase, TagResponse, NoteGenerateRequest, AIGeneratedNote
from app.services.note_service import NoteService
from app.services.gemini_service import GeminiService
from google import genai
from app.config.config import settings

router = APIRouter()

# --- Folders ---
@router.get("/folders", response_model=List[FolderResponse])
def get_folders(db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    return service.get_folders(int(current_user.id)) # type: ignore

@router.post("/folders", response_model=FolderResponse)
def create_folder(folder_in: FolderBase, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    return service.create_folder(int(current_user.id), folder_in) # type: ignore

@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    service.delete_folder(int(current_user.id), folder_id) # type: ignore
    return {"status": "success"}

# --- Tags ---
@router.get("/tags", response_model=List[TagResponse])
def get_tags(db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    return service.get_tags(int(current_user.id)) # type: ignore

@router.post("/tags", response_model=TagResponse)
def create_tag(tag_in: TagBase, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    return service.create_tag(int(current_user.id), tag_in) # type: ignore

@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    service.delete_tag(int(current_user.id), tag_id) # type: ignore
    return {"status": "success"}

# --- Notes ---
@router.get("/", response_model=List[NoteResponse])
def get_notes(
    folder_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    is_favorite: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(deps.get_db), 
    current_user: User = Depends(deps.get_current_user)
):
    service = NoteService(db)
    return service.get_notes(int(current_user.id), folder_id, tag_id, is_favorite, search) # type: ignore

@router.post("/", response_model=NoteResponse)
def create_note(note_in: NoteCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    return service.create_note(int(current_user.id), note_in) # type: ignore

@router.post("/generate", response_model=NoteResponse)
async def generate_general_note(request: NoteGenerateRequest, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    gemini = GeminiService()
    
    full_text = ""
    doc = None
    
    if request.document_id:
        from app.models.document import Document
        from app.models.processed_chunk import ProcessedChunk
        import uuid
        
        try:
            doc_uuid = uuid.UUID(request.document_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid document ID format")
        
        doc = db.query(Document).filter(Document.id == doc_uuid, Document.owner_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Selected document could not be found.")
        if doc.upload_status not in ["completed", "processed"]:
            raise HTTPException(status_code=400, detail="This document is still being processed. Please wait until processing is complete.")
            
        # RAG Logic
        from app.services.embedding import EmbeddingService
        from app.services.qdrant_service import QdrantService
        
        qdrant = QdrantService()
        embedding_service = EmbeddingService()
        
        if request.topic and request.topic.lower() != "document synthesis":
            try:
                # Use RAG to fetch relevant context
                query_vector = await embedding_service.generate_embeddings([request.topic])
                
                results = qdrant.search_embeddings(
                    query_vector=query_vector[0],
                    limit=20,
                    document_id=str(doc.id)
                )
                
                if results:
                    full_text = "\n\n".join([r['payload']['text_content'] for r in results])
            except Exception as e:
                print(f"RAG Retrieval failed: {e}")
                
        # Fallback if no topic or RAG fails/finds nothing
        if not full_text:
            chunks = db.query(ProcessedChunk).filter(ProcessedChunk.document_id == doc_uuid).order_by(ProcessedChunk.page_number, ProcessedChunk.chunk_index).all()
            if not chunks:
                raise HTTPException(status_code=400, detail="No relevant content was found for this topic.")
                
            full_text = "\n\n".join([chunk.text_content for chunk in chunks])
            if len(full_text) > 3000000:
                full_text = full_text[:3000000] + "\n\n[DOCUMENT TRUNCATED DUE TO EXTREME LENGTH LIMITS]"
    
    system_prompt = """You are an expert academic tutor.
Generate highly detailed, comprehensive study notes from the provided source material.
Do not produce a short summary. Ensure the notes are deeply structured and cover every facet of the topic.
You MUST organize the notes into the following sections whenever supported by the source material:
1. Introduction
2. Definitions
3. Core Concepts
4. Detailed Explanations
5. Working Principles
6. Types / Classifications
7. Examples
8. Applications
9. Advantages
10. Disadvantages
11. Key Points
12. Summary

Explain every important concept, process, component, principle, and formula.
Preserve the meaning and terminology of the source. Do not invent unsupported facts.
Explain concepts progressively from basic to advanced. The notes should be useful for rigorous university examination preparation.

Generate the output EXACTLY matching the JSON schema provided, ensuring 'sections' cover all detailed explanations, 'key_points' contains summary/revision points, and 'source_references' lists source concepts.
"""
    
    user_prompt = f"Topic to generate notes for: {request.topic}\n"
    if full_text:
        user_prompt += f"\nSource Material Context:\n{full_text}"
    if request.instructions:
        user_prompt += f"\nAdditional Instructions from User:\n{request.instructions}"

    try:
        json_data = gemini.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=AIGeneratedNote
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="The AI service could not generate the notes. Please try again.")

    # Reconstruct HTML from JSON
    html_content = ""
    import re
    
    def slugify(text):
        return re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
        
    for idx, sec in enumerate(json_data.get('sections', [])):
        title = sec.get('title', '')
        slug = slugify(title) or f"section-{idx}"
        html_content += f'<h2 id="{slug}">{title}</h2>\n'
        html_content += f"<div>{sec.get('content', '')}</div>\n"
        
    if json_data.get('key_points'):
        html_content += '<h2 id="important-points-final-summary">Important Points / Final Summary</h2>\n<ul>\n'
        for kp in json_data.get('key_points', []):
            html_content += f"<li>{kp}</li>\n"
        html_content += "</ul>\n"
        
    if json_data.get('source_references'):
        html_content += '<h2 id="source-references">Source References</h2>\n<ul>\n'
        for ref in json_data.get('source_references', []):
            html_content += f"<li>{ref}</li>\n"
        html_content += "</ul>\n"
        
    title = json_data.get('title', f"Notes on: {doc.filename if doc else request.topic}")

    # Save to db
    try:
        note_in = NoteCreate(
            title=title,
            topic=json_data.get('topic', request.topic),
            note_type=request.note_type,
            content=html_content,
            folder_id=request.folder_id,
            document_id=request.document_id
        )
        return service.create_note(int(current_user.id), note_in) # type: ignore
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Notes DB Save Error: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=f"Save Error: {e} | Trace: {tb}")

@router.get("/documents/{document_id}", response_model=List[NoteResponse])
def get_document_notes(document_id: str, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    query = db.query(Note).filter(Note.owner_id == current_user.id, Note.document_id == document_id)
    return query.order_by(Note.created_at.desc()).all()

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    return service.get_note(int(current_user.id), note_id) # type: ignore

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_in: NoteUpdate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    return service.update_note(int(current_user.id), note_id, note_in) # type: ignore

@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    service.delete_note(int(current_user.id), note_id) # type: ignore
    return {"status": "success"}

@router.post("/{note_id}/favorite", response_model=NoteResponse)
def toggle_favorite(note_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = NoteService(db)
    return service.toggle_favorite(int(current_user.id), note_id) # type: ignore
