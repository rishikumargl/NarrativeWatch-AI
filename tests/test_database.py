"""Tests for PostgreSQL client and models."""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.postgres_client import PostgresClient
from src.database.models import (
    InstagramPost, InstagramPage, Campaign, BiasPattern, AnalysisResult, Base
)
from sqlalchemy.orm import Session


@pytest.fixture
def client():
    """Create a test database client."""
    client = PostgresClient()
    # Create tables for testing
    Base.metadata.drop_all(bind=client.engine)
    Base.metadata.create_all(bind=client.engine)
    yield client
    # Cleanup
    Base.metadata.drop_all(bind=client.engine)
    client.close()


@pytest.fixture
def session(client):
    """Get a database session for testing."""
    return client.get_session()


class TestPostgresClient:
    """Test PostgreSQL client functionality."""

    def test_connection(self, client):
        """Test database connection."""
        assert client.engine is not None
        assert client.SessionLocal is not None

    def test_pgvector_extension(self, client):
        """Test pgvector extension is available."""
        has_pgvector = client.check_pgvector_extension()
        assert has_pgvector is True

    def test_create_tables(self, client):
        """Test tables are created."""
        with client.get_session() as session:
            # Check tables exist
            inspector = __import__('sqlalchemy').inspect(client.engine)
            tables = inspector.get_table_names()

            assert 'instagram_posts' in tables
            assert 'instagram_pages' in tables
            assert 'campaigns' in tables
            assert 'bias_patterns' in tables
            assert 'analysis_results' in tables


class TestInstagramPostModel:
    """Test InstagramPost model."""

    def test_create_post(self, session):
        """Test creating an Instagram post."""
        post = InstagramPost(
            post_id="123456789",
            page_username="test_page",
            caption="Test caption",
            hashtags=["#test", "#python"],
            content_type="image",
            posting_time=datetime.utcnow(),
            likes=100,
            comments=10,
            engagement_rate=0.5,
            trust_score=75.0,
        )

        session.add(post)
        session.commit()

        # Verify it was created
        retrieved = session.query(InstagramPost).filter_by(post_id="123456789").first()
        assert retrieved is not None
        assert retrieved.caption == "Test caption"
        assert retrieved.likes == 100

    def test_post_with_embedding(self, session):
        """Test storing post with vector embedding."""
        embedding = [0.1] * 1536  # Vector of 1536 dimensions

        post = InstagramPost(
            post_id="987654321",
            page_username="test_page2",
            caption="Post with embedding",
            embedding=embedding,
            posting_time=datetime.utcnow(),
            trust_score=50.0,
        )

        session.add(post)
        session.commit()

        retrieved = session.query(InstagramPost).filter_by(post_id="987654321").first()
        assert retrieved is not None
        assert retrieved.embedding is not None
        assert len(retrieved.embedding) == 1536


class TestInstagramPageModel:
    """Test InstagramPage model."""

    def test_create_page(self, session):
        """Test creating an Instagram page."""
        page = InstagramPage(
            page_id="page_123",
            username="test_influencer",
            display_name="Test Influencer",
            biography="This is a test page",
            account_type="creator",
            followers=10000,
            following=500,
            post_count=50,
            average_engagement_rate=0.05,
        )

        session.add(page)
        session.commit()

        retrieved = session.query(InstagramPage).filter_by(page_id="page_123").first()
        assert retrieved is not None
        assert retrieved.username == "test_influencer"
        assert retrieved.followers == 10000

    def test_page_unique_username(self, session):
        """Test username uniqueness constraint."""
        page1 = InstagramPage(
            page_id="page_1",
            username="unique_name",
        )
        page2 = InstagramPage(
            page_id="page_2",
            username="unique_name",  # Duplicate
        )

        session.add(page1)
        session.commit()

        session.add(page2)
        with pytest.raises(Exception):  # Should raise integrity error
            session.commit()


class TestCampaignModel:
    """Test Campaign model."""

    def test_create_campaign(self, session):
        """Test creating a campaign."""
        campaign = Campaign(
            campaign_id="campaign_001",
            campaign_name="Test Campaign",
            narrative_theme="Misinformation about election",
            pages_involved=["page_123", "page_456"],
            page_count=2,
            hashtags_used=["#fake", "#news"],
            coordination_score=0.85,
            severity_level="high",
        )

        session.add(campaign)
        session.commit()

        retrieved = session.query(Campaign).filter_by(campaign_id="campaign_001").first()
        assert retrieved is not None
        assert retrieved.page_count == 2
        assert retrieved.coordination_score == 0.85


class TestBiasPatternModel:
    """Test BiasPattern model."""

    def test_create_bias_pattern(self, session):
        """Test creating a bias pattern."""
        pattern = BiasPattern(
            pattern_id="bias_001",
            bias_category="political_right",
            pattern_description="Right-wing political bias indicators",
            indicators=["conservative", "anti-left", "traditional values"],
            frequency_score=0.7,
            severity_score=0.6,
        )

        session.add(pattern)
        session.commit()

        retrieved = session.query(BiasPattern).filter_by(pattern_id="bias_001").first()
        assert retrieved is not None
        assert retrieved.bias_category == "political_right"
        assert len(retrieved.indicators) == 3


class TestAnalysisResultModel:
    """Test AnalysisResult model."""

    def test_create_analysis_result(self, session):
        """Test creating an analysis result."""
        result = AnalysisResult(
            result_id="analysis_001",
            analysis_type="post",
            target_id="123456789",
            agents_used=["ContentAnalyzer", "BiasDetector", "BotDetector"],
            trust_score=72.5,
            reviewer_approved=1,
            confidence_level=0.95,
        )

        session.add(result)
        session.commit()

        retrieved = session.query(AnalysisResult).filter_by(result_id="analysis_001").first()
        assert retrieved is not None
        assert retrieved.trust_score == 72.5
        assert retrieved.reviewer_approved == 1


class TestDatabaseIndexes:
    """Test that indexes are created."""

    def test_indexes_exist(self, client):
        """Test that indexes are created for performance."""
        inspector = __import__('sqlalchemy').inspect(client.engine)

        # Check indexes on instagram_posts
        posts_indexes = inspector.get_indexes('instagram_posts')
        index_names = [idx['name'] for idx in posts_indexes]
        assert 'idx_instagram_posts_page_username' in index_names
        assert 'idx_instagram_posts_trust_score' in index_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
