"""PostgreSQL connection and management."""

import os
from typing import Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)


class PostgresClient:
    """PostgreSQL connection manager with connection pooling."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize PostgreSQL client.

        Args:
            database_url: PostgreSQL connection URL.
                         If None, reads from DATABASE_URL env var.
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/narrativewatch"
        )

        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        logger.info(f"Connecting to PostgreSQL: {self.database_url.split('@')[1]}")

        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            echo=False,
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

        self._test_connection()

    def _test_connection(self):
        """Test database connection."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("✓ PostgreSQL connection successful")
        except Exception as e:
            logger.error(f"✗ PostgreSQL connection failed: {e}")
            raise

    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()

    def create_all_tables(self):
        """Create all database tables."""
        from .models import Base
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("✓ Database tables created")

    def drop_all_tables(self):
        """Drop all database tables (for testing)."""
        from .models import Base
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("✓ Database tables dropped")

    def check_pgvector_extension(self) -> bool:
        """Check if pgvector extension is installed."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
                )
                has_extension = result.scalar()
                if has_extension:
                    logger.info("✓ pgvector extension found")
                    return True
                else:
                    logger.warning("✗ pgvector extension not found")
                    return False
        except Exception as e:
            logger.error(f"Error checking pgvector: {e}")
            return False

    def install_pgvector_extension(self):
        """Install pgvector extension."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                connection.commit()
                logger.info("✓ pgvector extension installed")
        except Exception as e:
            logger.error(f"Error installing pgvector: {e}")
            raise

    def close(self):
        """Close all database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global client instance
_client: Optional[PostgresClient] = None


def get_client() -> PostgresClient:
    """Get or create global PostgreSQL client."""
    global _client
    if _client is None:
        _client = PostgresClient()
    return _client


def get_session() -> Session:
    """Get a database session."""
    return get_client().get_session()
