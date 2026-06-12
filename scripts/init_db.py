#!/usr/bin/env python
"""Initialize PostgreSQL database with pgvector extension and tables."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.postgres_client import PostgresClient
from src.database.models import Base
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with pgvector and create all tables."""

    logger.info("=" * 80)
    logger.info("NARRATIVEWATCH AI - DATABASE INITIALIZATION")
    logger.info("=" * 80)

    try:
        # Create client and connect (will auto-create database if needed)
        logger.info("\n1. Connecting to PostgreSQL and creating database if needed...")
        client = PostgresClient()

        # Check pgvector extension
        logger.info("\n2. Checking pgvector extension...")
        if not client.check_pgvector_extension():
            logger.info("   Installing pgvector extension...")
            client.install_pgvector_extension()
        else:
            logger.info("   ✓ pgvector extension already installed")

        # Create tables
        logger.info("\n3. Creating database tables...")
        logger.info("   Tables to create:")
        logger.info("   - instagram_posts")
        logger.info("   - instagram_pages")
        logger.info("   - campaigns")
        logger.info("   - bias_patterns")
        logger.info("   - analysis_results")

        client.create_all_tables()

        logger.info("\n" + "=" * 80)
        logger.info("✓ DATABASE INITIALIZATION SUCCESSFUL!")
        logger.info("=" * 80)
        logger.info("\nDatabase is ready for use:")
        logger.info("  - PostgreSQL: running")
        logger.info("  - pgvector: installed")
        logger.info("  - Tables: created")
        logger.info("\nYou can now use the NarrativeWatch AI system.")
        logger.info("=" * 80)

        client.close()
        return 0

    except Exception as e:
        logger.error("\n" + "=" * 80)
        logger.error("✗ DATABASE INITIALIZATION FAILED!")
        logger.error("=" * 80)
        logger.error(f"\nError: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Check PostgreSQL is running:")
        logger.error("   docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:latest")
        logger.error("2. Check DATABASE_URL environment variable")
        logger.error("3. Check credentials in .env file")
        logger.error("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = init_database()
    sys.exit(exit_code)
