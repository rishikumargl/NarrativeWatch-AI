"""Run database migrations for authentication."""

import os
import logging
from sqlalchemy import text, create_engine
from src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Execute all pending migrations."""
    config = Config()
    engine = create_engine(config.DATABASE_URL)

    migration_file = os.path.join(os.path.dirname(__file__), "migration_users.sql")

    try:
        with engine.connect() as conn:
            with open(migration_file, 'r') as f:
                migration_sql = f.read()

            # Execute migration SQL
            conn.execute(text(migration_sql))
            conn.commit()

            logger.info("✅ Migrations executed successfully")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_migrations()
