from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
class Settings(BaseSettings):
    PROJECT_NAME: str = "EduAgent AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "eduagent_db"
    POSTGRES_PORT: int = 5432
    
    # JWT Authentication Settings
    # Run `openssl rand -hex 32` to generate a secure key
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Document Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # DOCX
        "application/vnd.openxmlformats-officedocument.presentationml.presentation" # PPTX
    ]
    
    # Chunking Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # AI Provider Settings
    AI_PROVIDER: str = "openai" # "openai" or "gemini"
    
    # OpenAI Settings
    OPENAI_API_KEY: str = "sk-placeholder-replace-with-real-key"
    
    # Gemini Settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    
    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "eduagent_chunks"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./eduagent.db"
    
    @property
    def DATABASE_URI(self) -> str:
        return self.DATABASE_URL
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

# Create a global instance of the settings object
settings = Settings()
