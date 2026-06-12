"""Configuration management for NarrativeWatch AI."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    APP_NAME: str = "NarrativeWatch AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, alias="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")

    # Database - PostgreSQL + pgvector
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/narrativewatch",
        alias="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, alias="DATABASE_ECHO")
    DATABASE_POOL_SIZE: int = Field(default=20, alias="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, alias="DATABASE_MAX_OVERFLOW")

    # LLM - Vertex AI (Primary)
    VERTEX_AI_PROJECT_ID: str = Field(default="", alias="VERTEX_AI_PROJECT_ID")
    VERTEX_AI_LOCATION: str = Field(default="us-central1", alias="VERTEX_AI_LOCATION")
    VERTEX_AI_MODEL: str = Field(default="gemini-2.5-pro", alias="VERTEX_AI_MODEL")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(
        default=None, alias="GOOGLE_APPLICATION_CREDENTIALS"
    )

    # LLM - Backup (Claude)
    CLAUDE_API_KEY: Optional[str] = Field(default=None, alias="CLAUDE_API_KEY")
    CLAUDE_MODEL: str = Field(default="claude-opus-4-8", alias="CLAUDE_MODEL")

    # LLM - Backup (OpenAI)
    OPENAI_API_KEY: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo", alias="OPENAI_MODEL")

    # LLM Provider selection
    LLM_PROVIDER: str = Field(default="vertex", alias="LLM_PROVIDER")

    # Embeddings
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-005", alias="EMBEDDING_MODEL"
    )
    EMBEDDING_DIMENSION: int = Field(default=768, alias="EMBEDDING_DIMENSION")

    # External APIs
    TAVILY_API_KEY: str = Field(default="", alias="TAVILY_API_KEY")
    INSTAGRAM_ACCESS_TOKEN: str = Field(default="", alias="INSTAGRAM_ACCESS_TOKEN")
    TWITTER_BEARER_TOKEN: Optional[str] = Field(
        default=None, alias="TWITTER_BEARER_TOKEN"
    )
    NEWSGUARD_API_KEY: Optional[str] = Field(
        default=None, alias="NEWSGUARD_API_KEY"
    )

    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = Field(default=5, alias="AGENT_MAX_ITERATIONS")
    AGENT_TIMEOUT_SECONDS: int = Field(default=120, alias="AGENT_TIMEOUT_SECONDS")
    AGENT_VERBOSE: bool = Field(default=False, alias="AGENT_VERBOSE")

    # Reflection Loop
    REFLECTION_MAX_RETRIES: int = Field(default=3, alias="REFLECTION_MAX_RETRIES")
    REFLECTION_TIMEOUT_SECONDS: int = Field(default=300, alias="REFLECTION_TIMEOUT_SECONDS")

    # RAG Configuration
    RAG_TOP_K: int = Field(default=5, alias="RAG_TOP_K")
    RAG_SIMILARITY_THRESHOLD: float = Field(
        default=0.7, alias="RAG_SIMILARITY_THRESHOLD"
    )

    # API Service
    API_HOST: str = Field(default="0.0.0.0", alias="API_HOST")
    API_PORT: int = Field(default=8000, alias="API_PORT")
    API_WORKERS: int = Field(default=4, alias="API_WORKERS")
    API_RELOAD: bool = Field(default=False, alias="API_RELOAD")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost", "http://localhost:3000", "http://localhost:8000"],
        alias="CORS_ORIGINS"
    )

    # Cache
    CACHE_ENABLED: bool = Field(default=True, alias="CACHE_ENABLED")
    CACHE_TTL_SECONDS: int = Field(default=3600, alias="CACHE_TTL_SECONDS")

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Global settings instance
settings = Settings()
