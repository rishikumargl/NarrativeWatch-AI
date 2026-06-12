"""Configuration management for NarrativeWatch AI."""

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Base configuration."""

    # Environment
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Application
    APP_NAME = "NarrativeWatch AI"
    APP_VERSION = "1.0.0"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

    # API Server
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    API_RELOAD = os.getenv("API_RELOAD", "False").lower() == "true"

    # LLM Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # API Keys
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/narrativewatch"
    )
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "narrativewatch")

    # Vector Database
    VECTOR_DIMENSION = 1536  # Vertex AI text-embedding-005 dimension

    # Agent Configuration
    MAX_AGENT_ITERATIONS = 5
    AGENT_TIMEOUT = 300  # 5 minutes
    REFLECTION_MAX_RETRIES = 3

    # Performance
    CACHE_TTL = 3600  # 1 hour
    BATCH_SIZE = 32

    # NLP Models
    SPACY_MODEL = "en_core_web_sm"
    SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
    BIAS_DETECTION_MODEL = "cardiffnlp/twitter-xlm-roberta-base"

    # Thresholds
    EMOTIONAL_LANGUAGE_THRESHOLD = 0.5
    BIAS_SCORE_THRESHOLD = 0.6
    BOT_ACTIVITY_THRESHOLD = 0.7
    TOXICITY_THRESHOLD = 0.5

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/narrativewatch.log")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_config() -> Config:
    """Get configuration instance."""
    return Config()


# Module-level instance for easy import
settings = get_config()
