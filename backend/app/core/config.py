from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Seoul Asan Hospital IDP"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/asan_idp"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:8501", "http://localhost:3000", "http://localhost:5173"]
    
    # AI/LLM
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Vector Database
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    QDRANT_URL: str = "http://localhost:6333"
    
    # HumanLayer Integration
    HUMANLAYER_API_KEY: Optional[str] = None
    HUMANLAYER_DAEMON_URL: str = "http://localhost:8080"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()