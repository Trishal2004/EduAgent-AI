from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy import Uuid as UUID

# Junction table for Topics and Skills
topic_skills = Table(
    "kg_topic_skills",
    Base.metadata,
    Column("topic_id", Integer, ForeignKey("kg_topics.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("kg_skills.id", ondelete="CASCADE"), primary_key=True)
)

class Topic(Base):
    __tablename__ = "kg_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    difficulty = Column(Integer, default=1) # 1-5
    mastery_level = Column(String(255), default="current") # mastered, revision, weak, current
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True) # Optional source
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", backref="kg_topics")
    skills = relationship("Skill", secondary=topic_skills, back_populates="topics")
    
    # Relationships where this topic is the source
    outgoing_relationships = relationship(
        "Relationship", 
        foreign_keys="[Relationship.source_id]",
        back_populates="source",
        cascade="all, delete-orphan"
    )
    
    # Relationships where this topic is the target
    incoming_relationships = relationship(
        "Relationship",
        foreign_keys="[Relationship.target_id]",
        back_populates="target",
        cascade="all, delete-orphan"
    )

class Relationship(Base):
    __tablename__ = "kg_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("kg_topics.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey("kg_topics.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(255), default="related_to") # prerequisite, related_to, part_of
    
    source = relationship("Topic", foreign_keys=[source_id], back_populates="outgoing_relationships")
    target = relationship("Topic", foreign_keys=[target_id], back_populates="incoming_relationships")

class Skill(Base):
    __tablename__ = "kg_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    
    topics = relationship("Topic", secondary=topic_skills, back_populates="skills")
