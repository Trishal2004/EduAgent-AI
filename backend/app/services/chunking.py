from typing import List
from app.config.config import settings

class ChunkingService:
    """
    A pure Python, recursive character text splitter.
    Splits text semantically to avoid cutting sentences in half.
    """
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        # Preference order for splitting boundaries
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        if not text:
            return final_chunks
            
        if len(text) <= self.chunk_size:
            return [text]
            
        separator = separators[-1] 
        for s in separators:
            if s == "":
                break
            if s in text:
                separator = s
                break
                
        splits = text.split(separator) if separator else list(text)
        
        current_chunk = []
        current_length = 0
        
        for s in splits:
            if current_length + len(s) + len(separator) > self.chunk_size and current_chunk:
                merged_text = separator.join(current_chunk).strip()
                if merged_text:
                    final_chunks.append(merged_text)
                
                # Overlap logic: keep end items of current chunk for the start of the next
                overlap_length = 0
                overlap_chunk = []
                for prev in reversed(current_chunk):
                    if overlap_length + len(prev) + len(separator) <= self.chunk_overlap:
                        overlap_chunk.insert(0, prev)
                        overlap_length += len(prev) + len(separator)
                    else:
                        break
                        
                current_chunk = overlap_chunk
                current_length = overlap_length
                
            current_chunk.append(s)
            current_length += len(s) + (len(separator) if current_length > 0 else 0)
            
        if current_chunk:
            merged_text = separator.join(current_chunk).strip()
            if merged_text:
                final_chunks.append(merged_text)
                
        # Recursively split chunks that are still too large
        next_separators = separators[separators.index(separator) + 1:] if separator in separators else []
        if next_separators:
            recursive_chunks = []
            for chunk in final_chunks:
                if len(chunk) > self.chunk_size:
                    recursive_chunks.extend(self._split_text(chunk, next_separators))
                else:
                    recursive_chunks.append(chunk)
            return recursive_chunks
            
        return final_chunks

    def chunk_text(self, text: str) -> List[str]:
        """Public method to split a long string into overlapping chunks."""
        return self._split_text(text, self.separators)
