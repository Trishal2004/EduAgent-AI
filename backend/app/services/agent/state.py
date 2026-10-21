from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    """
    Represents the state of our RAG agent throughout its execution loop.
    """
    original_question: str
    document_id: str
    search_query: str
    require_retrieval: bool
    context: List[Dict[str, Any]]
    context_quality_score: str # "good" or "poor"
    retrieval_attempts: int
    answer: Any # Will hold the StructuredAnswer dict or standard text
    citations: List[Dict[str, Any]]
    chat_history: List[Dict[str, str]]
    stream_queue: Any
    image_data: Optional[str]
    allowed_document_ids: List[str]
    document_names: Dict[str, str]
