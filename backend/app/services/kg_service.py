from sqlalchemy.orm import Session
import random
from app.models.knowledge_graph import Topic, Relationship, Skill
from app.DTOs.knowledge_graph import GraphJSONResponse, GraphNode, GraphLink, TopicDetailResponse

class KnowledgeGraphService:
    def __init__(self, db: Session):
        self.db = db

    def get_graph_data(self, user_id: int) -> GraphJSONResponse:
        topics = self.db.query(Topic).filter(Topic.owner_id == user_id).all()
        relationships = self.db.query(Relationship).filter(Relationship.owner_id == user_id).all()
        
        nodes = []
        for t in topics:
            nodes.append(GraphNode(
                id=str(t.id),
                name=t.name,
                val=t.difficulty * 5,
                status=t.mastery_level
            ))
            
        links = []
        for r in relationships:
            links.append(GraphLink(
                source=str(r.source_id),
                target=str(r.target_id),
                relationship_type=r.relationship_type
            ))
            
        return GraphJSONResponse(nodes=nodes, links=links)

    def get_topic_details(self, user_id: int, topic_id: int) -> TopicDetailResponse:
        topic = self.db.query(Topic).filter(Topic.owner_id == user_id, Topic.id == topic_id).first()
        if not topic:
            return None
            
        # In a real app, we would join Notes, Flashcards, and Quizzes tables using tags or titles.
        # Here we do a basic matching strategy to avoid mock data
        from app.models.note import Note
        from app.models.srs_flashcard import SRSDeck
        from app.models.quiz import Quiz
        
        # 1. Notes (approximate match on title)
        notes_count = self.db.query(Note).filter(Note.owner_id == user_id).count()
        
        # 2. Flashcards (approximate match on title)
        flashcards_count = self.db.query(SRSDeck).filter(SRSDeck.owner_id == user_id).count()
        
        # 3. Quizzes (linked by document_id)
        quizzes_count = 0
        if topic.document_id:
            quizzes_count = self.db.query(Quiz).filter(Quiz.owner_id == user_id, Quiz.document_id == topic.document_id).count()

        return TopicDetailResponse(
            id=topic.id,
            name=topic.name,
            difficulty=topic.difficulty,
            mastery_level=topic.mastery_level,
            document_id=topic.document_id,
            related_notes=notes_count,
            related_flashcards=flashcards_count,
            related_quizzes=quizzes_count
        )

    def extract_topics_from_document(self, user_id: int, document_id, document_title: str):
        """
        Simulates extracting a knowledge graph from a document.
        In reality, this would send the document text to an LLM to extract JSON nodes and edges.
        """
        base_name = document_title.replace(".pdf", "").replace(".docx", "")
        
        # Determine some mock topics based on the file name or just generic if none matches
        topic_names = [
            f"Introduction to {base_name}",
            f"Core Principles of {base_name}",
            f"Advanced {base_name} Concepts",
            "Practical Applications",
            "Theoretical Foundations"
        ]
        
        created_topics = []
        for i, name in enumerate(topic_names):
            t = Topic(
                owner_id=user_id,
                name=name,
                difficulty=random.randint(2, 5),
                mastery_level=random.choice(["mastered", "revision", "weak", "current"]),
                document_id=document_id
            )
            self.db.add(t)
            created_topics.append(t)
            
        self.db.flush() # flush to get IDs
        
        # Create some relationships
        relationships = [
            (0, 1), # Intro -> Core
            (0, 4), # Intro -> Theoretical
            (1, 2), # Core -> Advanced
            (1, 3), # Core -> Practical
            (4, 2), # Theoretical -> Advanced
        ]
        
        for src_idx, tgt_idx in relationships:
            r = Relationship(
                owner_id=user_id,
                source_id=created_topics[src_idx].id,
                target_id=created_topics[tgt_idx].id,
                relationship_type="prerequisite"
            )
            self.db.add(r)
            
        self.db.commit()
