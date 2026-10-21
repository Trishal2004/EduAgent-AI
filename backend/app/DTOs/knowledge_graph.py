from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class GraphNode(BaseModel):
    id: str # String ID for D3 compatibility (we will map topic ID to string)
    name: str
    val: int # Size of node, maps to difficulty (e.g. difficulty * 5)
    status: str # mastery_level (mastered, revision, weak, current)

class GraphLink(BaseModel):
    source: str # Source ID
    target: str # Target ID
    relationship_type: str

class GraphJSONResponse(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

class TopicDetailResponse(BaseModel):
    id: int
    name: str
    difficulty: int
    mastery_level: str
    document_id: Optional[UUID] = None
    related_notes: int = 0
    related_flashcards: int = 0
    related_quizzes: int = 0

    class Config:
        from_attributes = True
