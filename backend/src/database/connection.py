"""Database connection management for PostgreSQL + pgvector."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings
from src.logger import logger

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    from src.database.models import Base

    # Enable pgvector extension
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
