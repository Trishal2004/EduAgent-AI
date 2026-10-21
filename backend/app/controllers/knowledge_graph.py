from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.security import deps
from app.models.user import User
from app.DTOs.knowledge_graph import GraphJSONResponse, TopicDetailResponse
from app.services.kg_service import KnowledgeGraphService

router = APIRouter()

@router.get("/graph", response_model=GraphJSONResponse)
def get_graph(db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = KnowledgeGraphService(db)
    return service.get_graph_data(current_user.id)

@router.get("/topics/{topic_id}", response_model=TopicDetailResponse)
def get_topic_details(topic_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    service = KnowledgeGraphService(db)
    details = service.get_topic_details(current_user.id, topic_id)
    if not details:
        raise HTTPException(status_code=404, detail="Topic not found")
    return details
