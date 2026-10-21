from abc import ABC, abstractmethod
from typing import List
from app.DTOs.document_chunk import DocumentChunkCreate
from uuid import UUID

class BaseExtractor(ABC):
    """
    Abstract Base Class for all document extractors.
    Any new file format extractor must implement the extract() method.
    """
    
    @abstractmethod
    def extract(self, file_path: str, document_id: UUID) -> List[DocumentChunkCreate]:
        """
        Reads the file at file_path and extracts text into structural chunks.
        
        Args:
            file_path: Absolute path to the saved document.
            document_id: The UUID of the document record in the DB.
            
        Returns:
            A list of DocumentChunkCreate objects ready to be saved to DB.
        """
        pass
