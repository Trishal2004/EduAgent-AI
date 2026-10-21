from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from typing import List, Dict, Any
from uuid import UUID
from app.config.config import settings
from app.DTOs.processed_chunk import ProcessedChunkCreate

class QdrantService:
    def __init__(self):
        # Initialize client. 
        # In production, you might want this to be an async client or managed via dependency injection
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.is_connected = False
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Creates the collection if it doesn't already exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(col.name == self.collection_name for col in collections)
            if not exists:
                # 1536 is the dimension for text-embedding-3-small
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(
                        size=1536,
                        distance=rest.Distance.COSINE
                    )
                )
            self.is_connected = True
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant. Vector search will be disabled. Error: {e}")
            self.is_connected = False

    def insert_embeddings(self, chunks: List[ProcessedChunkCreate], embeddings: List[List[float]], chunk_ids: List[UUID]):
        """
        Inserts vectors and their associated metadata payloads into Qdrant.
        We use the UUID generated for PostgreSQL as the Qdrant Point ID for exact syncing.
        """
        if not self.is_connected:
            print("Warning: Qdrant is not connected. Skipping embedding insertion.")
            return

        points = []
        for chunk, embedding, chunk_id in zip(chunks, embeddings, chunk_ids):
            # Payload contains the metadata we want to filter or retrieve later
            payload = {
                "document_id": str(chunk.document_id),
                "page_number": chunk.page_number,
                "section_title": chunk.section_title,
                "text_content": chunk.text_content
            }
            
            points.append(
                rest.PointStruct(
                    id=str(chunk_id), # Qdrant supports UUIDs directly as strings
                    vector=embedding,
                    payload=payload
                )
            )
            
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    def search_embeddings(self, query_vector: List[float], limit: int = 5, document_id: str = None, allowed_document_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Searches for the closest vectors using Cosine Similarity.
        Optionally filters by document_id or a list of allowed_document_ids.
        """
        if settings.OPENAI_API_KEY == "YOUR_REAL_OPENAI_API_KEY":
            # Real vector search is disabled without a key. Return empty list to trigger the MySQL fallback.
            return []
        if not self.is_connected:
            raise Exception("Qdrant vector database is not connected. Cannot perform document search.")

        must_conditions = []
        if document_id:
            must_conditions.append(rest.FieldCondition(key="document_id", match=rest.MatchValue(value=document_id)))
        elif allowed_document_ids is not None:
            if not allowed_document_ids:
                return [] # No documents accessible
            must_conditions.append(rest.FieldCondition(key="document_id", match=rest.MatchAny(any=allowed_document_ids)))

        query_filter = rest.Filter(must=must_conditions) if must_conditions else None

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit
        )
        
        # Format results for easy consumption
        formatted = []
        for r in results:
            formatted.append({
                "id": r.id,
                "score": r.score,
                "payload": r.payload
            })
        return formatted

    def delete_embeddings_by_document(self, document_id: str):
        """Deletes all vectors associated with a specific document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=rest.FilterSelector(
                filter=rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="document_id",
                            match=rest.MatchValue(value=document_id)
                        )
                    ]
                )
            )
        )

    def update_embedding_payload(self, point_id: str, new_payload: Dict[str, Any]):
        """Updates the metadata payload of a specific vector point."""
        self.client.set_payload(
            collection_name=self.collection_name,
            payload=new_payload,
            points=[point_id]
        )
