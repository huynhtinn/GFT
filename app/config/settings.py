from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Cấu hình ứng dụng quản lý bởi Pydantic Settings đọc từ file .env."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # GENERAL APP SETTINGS
    APP_NAME: str = Field(default="Autonomous Customer Support Agent System")
    DEBUG: bool = Field(default=False)

    # GROQ LLM API SETTINGS
    GROQ_API_KEY: str = Field(default="", description="Groq Cloud API key")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Groq LLM model name")

    # QDRANT VECTOR DB SETTINGS
    QDRANT_URL: str = Field(default="http://localhost:6333", description="Qdrant DB Server URL")
    QDRANT_COLLECTION_NAME: str = Field(default="knowledge_base", description="Qdrant collection name")
    VECTOR_DIM: int = Field(default=384, description="Vector embedding dimension")
    QDRANT_TIMEOUT_SECONDS: float = Field(default=3.0, description="Qdrant connection timeout")

    # THRESHOLDS & RAG SETTINGS
    RAG_CONFIDENCE_THRESHOLD: float = Field(default=30.0, description="Ngưỡng tin cậy RAG % tối thiểu cho auto-resolve")
    RAG_SEARCH_LIMIT: int = Field(default=3, description="Số lượng trích đoạn tri thức cần lấy")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.GROQ_API_KEY:
        settings.GROQ_API_KEY = settings.GROQ_API_KEY.strip()
    return settings

# Singleton settings instance
settings = get_settings()
