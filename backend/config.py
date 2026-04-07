import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Documind Elite"
    VERSION: str = "2.2.0"
    DEBUG: bool = False
    
    # API Settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    ALLOWED_ORIGINS: List[str] = [FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Database Settings
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")
    CHROMA_CLOUD_HOST: str = os.getenv("CHROMA_CLOUD_HOST", "https://api.trychroma.com")
    CHROMA_API_KEY: str = os.getenv("CHROMA_API_KEY", "")
    CHROMA_TENANT: str = os.getenv("CHROMA_TENANT", "default")
    CHROMA_DATABASE: str = os.getenv("CHROMA_DATABASE", "default")
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "market_intelligence")
    
    # AI Provider Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # External Services
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Storage
    TEMP_DIR: str = "temp_pdfs"
    CACHE_DIR: str = ".ai_cache"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
