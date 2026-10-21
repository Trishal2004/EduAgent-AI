from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.qdrant_service import QdrantService
from app.services.embedding import EmbeddingService

router = APIRouter()

@router.post("/search")
async def search_qdrant(query: str, limit: int = 5, document_id: str = None):
    """
    TEST API: Embeds the query text and searches Qdrant.
    """
    emb_service = EmbeddingService()
    try:
        embeddings = await emb_service.generate_embeddings([query])
        query_vector = embeddings[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
        
    qdrant = QdrantService()
    results = qdrant.search_embeddings(query_vector, limit=limit, document_id=document_id)
    return {"results": results}

@router.delete("/delete/{document_id}")
async def delete_document_embeddings(document_id: str):
    """
    TEST API: Deletes all vectors for a specific document.
    """
    qdrant = QdrantService()
    qdrant.delete_embeddings_by_document(document_id)
    return {"message": f"Deleted all embeddings for document {document_id}"}

@router.put("/update/{chunk_id}")
async def update_embedding_metadata(chunk_id: str, new_title: str):
    """
    TEST API: Updates the payload (e.g., section_title) of a specific chunk.
    """
    qdrant = QdrantService()
    qdrant.update_embedding_payload(
        point_id=chunk_id,
        new_payload={"section_title": new_title}
    )
    return {"message": f"Updated metadata for chunk {chunk_id}"}
