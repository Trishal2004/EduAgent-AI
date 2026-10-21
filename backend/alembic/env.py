import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import our settings and base model
from app.config.config import settings
from app.db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
from app.models.user import User
from app.models.document import Document, PDFMetadata
from app.models.workspace import Workspace, RecentFile, PinnedDocument, RecentActivity
from app.models.mentor import MentorStudyPlan, Recommendation, WeakTopic, Goal, MentorChat
from app.models.document_chunk import DocumentChunk
from app.models.processed_chunk import ProcessedChunk
from app.models.study_note import StudyNote
from app.models.flashcard import FlashcardDeck, Flashcard
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt
from app.models.question_paper import QuestionPaper
from app.models.dashboard import DashboardProfile
from app.models.tutor import TutorSession, ChatMessage
from app.models.course import Course, Lesson, Enrollment, Progress
from app.models.analytics import Analytics, StudySession, QuizResult, Performance
from app.models.note import Folder, Tag, Note
from app.models.srs_flashcard import SRSDeck, SRSCard, ReviewHistory
from app.models.knowledge_graph import Topic, Relationship, Skill
from app.models.otp import UserLoginOTP
import pgvector.sqlalchemy
target_metadata = Base.metadata

import os
from dotenv import load_dotenv

load_dotenv()

def get_url():
    """Retrieve the database URL from our config"""
    return os.getenv("DATABASE_URL")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    from sqlalchemy import engine_from_config
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
