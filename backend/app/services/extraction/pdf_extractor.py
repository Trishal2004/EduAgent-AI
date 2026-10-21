import fitz  # PyMuPDF
from typing import List
from uuid import UUID
from app.services.extraction.base import BaseExtractor
from app.DTOs.document_chunk import DocumentChunkCreate

class PDFExtractor(BaseExtractor):
    def extract(self, file_path: str, document_id: UUID) -> List[DocumentChunkCreate]:
        chunks = []
        doc = fitz.open(file_path)
        
        # Simple extraction: one chunk per page.
        # Advanced implementations would look at doc.get_toc() for sections, 
        # or use doc.get_text("blocks") for paragraph-level chunking.
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text").strip()
            
            if text:
                chunks.append(
                    DocumentChunkCreate(
                        document_id=document_id,
                        page_number=page_num + 1,  # 1-indexed for humans
                        section_title=f"Page {page_num + 1}",
                        text_content=text,
                        extracted_metadata={"source_type": "pdf_page"}
                    )
                )
                
        doc.close()
        return chunks
