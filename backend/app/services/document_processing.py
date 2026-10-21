from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import HTTPException, status
from uuid import UUID
import os

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.processed_chunk import ProcessedChunk
from app.repositories.document_chunk import DocumentChunkRepository
from app.repositories.processed_chunk import ProcessedChunkRepository
from app.services.extraction.factory import ExtractionFactory
from app.services.chunking import ChunkingService
from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.DTOs.document_chunk import ProcessingResponse
from app.DTOs.processed_chunk import ProcessedChunkCreate

class DocumentProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.chunk_repo = DocumentChunkRepository(db)
        self.processed_chunk_repo = ProcessedChunkRepository(db)
        self.chunker = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    async def process_document(self, document_id: UUID, owner_id: UUID) -> ProcessingResponse:
        """
        Coordinates fetching the document, running the appropriate extractor,
        saving the chunks to the database, and updating the document status.
        """
        try:
                # 1. Fetch document and verify ownership
            result = self.db.execute(select(Document).where(Document.id == document_id))
            doc = result.scalars().first()
        
            if not doc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            if doc.owner_id != owner_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to process this document")
            if doc.upload_status == "processed":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document already processed")
            
            if not os.path.exists(doc.file_path):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file not found on disk")

            # 2. Extract content
            try:
                extractor = ExtractionFactory.get_extractor(doc.content_type)
                chunks = extractor.extract(doc.file_path, doc.id)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            except Exception as e:
                # Mark as failed in DB
                doc.upload_status = "failed"
                self.db.commit()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Extraction failed: {str(e)}")

            # 3. Save raw chunks to DB
            saved_raw_chunks = self.chunk_repo.create_many(chunks)
        
            # 4. Perform Semantic Chunking for Vector Embeddings
            # We need the generated UUIDs from saved_raw_chunks.
            # Since create_many doesn't currently return the models in our implementation,
            # we will fetch them or modify create_many to return them.
            # For this pipeline, we will chunk them in memory and let processed_chunks hold the pieces.
            # *Note*: To link `parent_chunk_id` we must commit and fetch the raw chunks first.
        
            # Let's commit to get IDs for raw chunks
            self.db.commit()
        
            # Fetch the raw chunks just inserted for this document
            result = self.db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document_id))
            raw_db_chunks = result.scalars().all()
        
            processed_chunks_to_save = []
            for raw_chunk in raw_db_chunks:
                # Sub-divide the raw extracted page/slide into semantic overlapping chunks
                sub_texts = self.chunker.chunk_text(raw_chunk.text_content)
                for idx, text in enumerate(sub_texts):
                    processed_chunks_to_save.append(
                        ProcessedChunkCreate(
                            document_id=doc.id,
                            parent_chunk_id=raw_chunk.id,
                            page_number=raw_chunk.page_number,
                            section_title=raw_chunk.section_title,
                            chunk_index=idx,
                            text_content=text
                        )
                    )
                
            # 5. Generate Vector Embeddings for all processed chunks
            texts_to_embed = [chunk.text_content for chunk in processed_chunks_to_save]
        
            embeddings = []
            try:
                if texts_to_embed:
                    embeddings = await self.embedding_service.generate_embeddings(texts_to_embed)
                
                    # Attach embeddings back to the schema objects
                    for chunk, embedding in zip(processed_chunks_to_save, embeddings):
                        chunk.embedding = embedding
            except Exception as e:
                doc.upload_status = "failed"
                self.db.commit()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate embeddings. Is your OpenAI API key valid? Error: {str(e)}")
                
            # 6. Save the overlapping semantic chunks WITH their embeddings to Postgres
            self.processed_chunk_repo.create_many(processed_chunks_to_save)
        
            # 7. Push to Qdrant!
            # Note: We must flush/commit Postgres to get the actual UUIDs if they were generated by the DB.
            # But we generated them in Python (`uuid4()`), so we already have `processed_chunks_to_save` with IDs if we modified the repo to return them.
            # Since our repo doesn't return them, let's fetch them from Postgres or generate them manually beforehand.
            # Wait, our `ProcessedChunkCreate` schema does NOT have an `id`. 
            # For simplicity, we will query them back from Postgres so we have the precise UUIDs.
            self.db.commit()
        
            # Fetch the newly created processed chunks
            result = self.db.execute(select(ProcessedChunk).where(ProcessedChunk.document_id == document_id))
            db_processed_chunks = result.scalars().all()
        
            if db_processed_chunks and embeddings:
                # Reconstruct schemas and ids
                qdrant_chunks = []
                chunk_ids = []
                for pc in db_processed_chunks:
                    qdrant_chunks.append(
                        ProcessedChunkCreate(
                            document_id=pc.document_id,
                            parent_chunk_id=pc.parent_chunk_id,
                            page_number=pc.page_number,
                            section_title=pc.section_title,
                            chunk_index=pc.chunk_index,
                            text_content=pc.text_content
                        )
                    )
                    chunk_ids.append(pc.id)
                
                # Run Qdrant insert (this is a synchronous call in our service)
                self.qdrant_service.insert_embeddings(
                    chunks=qdrant_chunks,
                    embeddings=embeddings,
                    chunk_ids=chunk_ids
                )
        
            # 8. Update document status
            doc.upload_status = "completed"
            doc.embedding_status = "completed"
            self.db.commit()
        
            return ProcessingResponse(
                message="Document processed and chunked successfully",
                document_id=doc.id,
                chunks_extracted=len(processed_chunks_to_save)
            )
        except Exception as global_e:
            import traceback
            with open("debug_error.log", "a") as f:
                f.write(f"\n--- ERROR ---\n{traceback.format_exc()}\n")
            raise HTTPException(status_code=500, detail=str(global_e))
