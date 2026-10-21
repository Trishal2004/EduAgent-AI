from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.controllers.api import api_router
from app.db.base import Base
from app.db.database import engine
from app.models import user, document, tutor, note, flashcard, srs_flashcard, quiz, question_paper, knowledge_graph, analytics, mentor, workspace, course, notification, study_plan, otp

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="EduAgent AI Backend",
    description="Backend for EduAgent AI Final Year Project",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to EduAgent AI API"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is healthy"}
