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

    # COHERE RERANKER SETTINGS
    COHERE_API_KEY: str = Field(default="", description="Cohere API key")
    COHERE_MODEL: str = Field(default="rerank-multilingual-v3.0", description="Cohere Rerank model name")
    USE_RERANK: bool = Field(default=True, description="Enable Cohere Reranker")

    # THRESHOLDS & RAG SETTINGS
    RAG_CONFIDENCE_THRESHOLD: float = Field(default=30.0, description="Ngưỡng tin cậy RAG % tối thiểu cho auto-resolve")
    RAG_SEARCH_LIMIT: int = Field(default=3, description="Số lượng trích đoạn tri thức cần lấy")
    RAG_CHUNK_SIZE: int = Field(default=800, description="Kích thước đoạn văn bản (ký tự) khi chia nhỏ tài liệu")
    RAG_CHUNK_OVERLAP: int = Field(default=50, description="Độ chồng chéo giữa các đoạn (ký tự)")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.GROQ_API_KEY:
        settings.GROQ_API_KEY = settings.GROQ_API_KEY.strip()
    if settings.COHERE_API_KEY:
        settings.COHERE_API_KEY = settings.COHERE_API_KEY.strip()
    return settings

# Singleton settings instance
settings = get_settings()
