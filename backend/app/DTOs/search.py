from pydantic import BaseModel
from typing import List, Optional

class SearchResultItem(BaseModel):
    id: str
    type: str # document, note, flashcard, course, quiz, chat
    title: str
    snippet: Optional[str] = None
    url: Optional[str] = None

class GlobalSearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]
