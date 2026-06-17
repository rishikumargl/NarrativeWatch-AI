import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
    PORT = int(os.getenv("FASTAPI_PORT", 8000))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://narrativewatch:password@localhost:5432/narrativewatch_ai")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 20))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    WEBSOCKET_ORIGINS = os.getenv("WEBSOCKET_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_REFLECTION_ITERATIONS = int(os.getenv("MAX_REFLECTION_ITERATIONS", 3))
    AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", 300))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    TOKEN_EXPIRE_DAYS = int(os.getenv("TOKEN_EXPIRE_DAYS", 7))

config = Config()
