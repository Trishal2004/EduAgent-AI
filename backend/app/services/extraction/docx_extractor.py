from docx import Document
from typing import List
from uuid import UUID
from app.services.extraction.base import BaseExtractor
from app.DTOs.document_chunk import DocumentChunkCreate

class DOCXExtractor(BaseExtractor):
    def extract(self, file_path: str, document_id: UUID) -> List[DocumentChunkCreate]:
        chunks = []
        doc = Document(file_path)
        
        current_section = "Document Start"
        current_text_block = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            # If the paragraph is a heading, it signifies a new section
            if para.style.name.startswith('Heading'):
                # Save the previous section if it has text
                if current_text_block:
                    chunks.append(
                        DocumentChunkCreate(
                            document_id=document_id,
                            section_title=current_section,
                            text_content="\n".join(current_text_block),
                            extracted_metadata={"source_type": "docx_section"}
                        )
                    )
                    current_text_block = []
                current_section = text
            else:
                current_text_block.append(text)
                
        # Don't forget the last block
        if current_text_block:
            chunks.append(
                DocumentChunkCreate(
                    document_id=document_id,
                    section_title=current_section,
                    text_content="\n".join(current_text_block),
                    extracted_metadata={"source_type": "docx_section"}
                )
            )
            
        return chunks
