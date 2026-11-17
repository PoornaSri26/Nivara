import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nivara"
    PROJECT_TAGLINE: str = "Understand your thoughts. Build your balance."
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nivara.db")
    
    # LLM Settings (OpenAI / Gemini / Anthropic compatible)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "mock-key")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gemini-1.5-pro")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-small")
    
    # Safety Thresholds
    SAFETY_STRICT_MODE: bool = True
    CRISIS_CONFIDENCE_THRESHOLD: float = 0.65
    
    # Memory Settings
    DEFAULT_MEMORY_CONFIDENCE_THRESHOLD: float = 0.70
    PROPOSED_MEMORY_EXPIRATION_DAYS: int = 14
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

