from app.services.extraction.base import BaseExtractor
from app.services.extraction.pdf_extractor import PDFExtractor
from app.services.extraction.docx_extractor import DOCXExtractor
from app.services.extraction.pptx_extractor import PPTXExtractor

class ExtractionFactory:
    """Factory to return the appropriate extractor based on MIME type."""
    
    @staticmethod
    def get_extractor(content_type: str) -> BaseExtractor:
        if content_type == "application/pdf":
            return PDFExtractor()
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return DOCXExtractor()
        elif content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            return PPTXExtractor()
        else:
            raise ValueError(f"No extractor available for content type: {content_type}")
