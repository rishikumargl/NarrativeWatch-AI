"""Tests for RAG pipeline."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.rag_pipeline import RAGPipeline, get_rag_pipeline


class TestRAGPipeline:
    """Test RAG pipeline."""

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_initialization(self, mock_api, mock_embedding, mock_db):
        """Test RAG pipeline initialization."""
        pipeline = RAGPipeline()
        assert pipeline.db_client is not None
        assert pipeline.embedding_client is not None
        assert pipeline.instagram_api is not None

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_ingest_instagram_post(self, mock_api, mock_embedding, mock_db):
        """Test ingesting Instagram post."""
        # Setup mocks
        mock_embedding_client = MagicMock()
        mock_embedding_client.embed_instagram_post.return_value = [0.1] * 1536
        mock_embedding.return_value = mock_embedding_client

        mock_session = MagicMock()
        mock_db.return_value.get_session.return_value = mock_session

        pipeline = RAGPipeline()
        post_id = pipeline.ingest_instagram_post(
            post_id="123",
            page_username="testuser",
            caption="Test caption",
            hashtags=["#test"],
        )

        assert post_id == "123"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_ingest_instagram_page(self, mock_api, mock_embedding, mock_db):
        """Test ingesting Instagram page."""
        mock_embedding_client = MagicMock()
        mock_embedding_client.embed_instagram_page.return_value = [0.1] * 1536
        mock_embedding.return_value = mock_embedding_client

        mock_session = MagicMock()
        mock_db.return_value.get_session.return_value = mock_session

        pipeline = RAGPipeline()
        page_id = pipeline.ingest_instagram_page(
            page_id="page_123",
            username="testuser",
            display_name="Test User",
            biography="Test bio",
        )

        assert page_id == "page_123"
        mock_session.add.assert_called_once()

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_ingest_bias_pattern(self, mock_api, mock_embedding, mock_db):
        """Test ingesting bias pattern."""
        mock_embedding_client = MagicMock()
        mock_embedding_client.embed_text.return_value = [0.1] * 1536
        mock_embedding.return_value = mock_embedding_client

        mock_session = MagicMock()
        mock_db.return_value.get_session.return_value = mock_session

        pipeline = RAGPipeline()
        pattern_id = pipeline.ingest_bias_pattern(
            pattern_id="pattern_123",
            bias_category="gender",
            pattern_description="Bias description",
            indicators=["indicator1"],
        )

        assert pattern_id == "pattern_123"
        mock_session.add.assert_called_once()

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_search_similar_posts(self, mock_api, mock_embedding, mock_db):
        """Test searching similar posts."""
        # Setup mocks
        mock_post = MagicMock()
        mock_post.post_id = "123"
        mock_post.caption = "Test caption"
        mock_post.page_username = "testuser"
        mock_post.trust_score = 0.8
        mock_post.hashtags = ["#test"]

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [
            (mock_post, 0.1)
        ]
        mock_session.query.return_value = mock_query
        mock_db.return_value.get_session.return_value = mock_session

        mock_embedding_client = MagicMock()
        mock_embedding.return_value = mock_embedding_client

        pipeline = RAGPipeline()
        results = pipeline.search_similar_posts(
            query_embedding=[0.1] * 1536,
            limit=5,
        )

        assert len(results) > 0
        assert results[0]["post_id"] == "123"

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_search_similar_pages(self, mock_api, mock_embedding, mock_db):
        """Test searching similar pages."""
        mock_page = MagicMock()
        mock_page.page_id = "page_123"
        mock_page.username = "testuser"
        mock_page.followers = 1000
        mock_page.average_trust_score = 0.7

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [
            (mock_page, 0.2)
        ]
        mock_session.query.return_value = mock_query
        mock_db.return_value.get_session.return_value = mock_session

        mock_embedding_client = MagicMock()
        mock_embedding.return_value = mock_embedding_client

        pipeline = RAGPipeline()
        results = pipeline.search_similar_pages(
            query_embedding=[0.1] * 1536,
            limit=5,
        )

        assert len(results) > 0
        assert results[0]["username"] == "testuser"

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_search_bias_patterns(self, mock_api, mock_embedding, mock_db):
        """Test searching bias patterns."""
        mock_pattern = MagicMock()
        mock_pattern.pattern_id = "pattern_123"
        mock_pattern.bias_category = "gender"
        mock_pattern.indicators = ["ind1"]
        mock_pattern.severity_score = 0.8

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [
            (mock_pattern, 0.15)
        ]
        mock_session.query.return_value = mock_query
        mock_db.return_value.get_session.return_value = mock_session

        mock_embedding_client = MagicMock()
        mock_embedding.return_value = mock_embedding_client

        pipeline = RAGPipeline()
        results = pipeline.search_bias_patterns(
            query_embedding=[0.1] * 1536,
            limit=5,
        )

        assert len(results) > 0
        assert results[0]["bias_category"] == "gender"

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_get_post_count(self, mock_api, mock_embedding, mock_db):
        """Test getting post count."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.scalar.return_value = 10
        mock_session.query.return_value = mock_query
        mock_db.return_value.get_session.return_value = mock_session

        mock_embedding_client = MagicMock()
        mock_embedding.return_value = mock_embedding_client

        pipeline = RAGPipeline()
        count = pipeline.get_post_count()

        assert count == 10

    @patch("src.database.rag_pipeline.get_client")
    @patch("src.database.rag_pipeline.get_embedding_client")
    @patch("src.database.rag_pipeline.InstagramAPI")
    def test_get_rag_stats(self, mock_api, mock_embedding, mock_db):
        """Test getting RAG stats."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.scalar.return_value = 10
        mock_session.query.return_value = mock_query
        mock_db.return_value.get_session.return_value = mock_session

        mock_embedding_client = MagicMock()
        mock_embedding_client.cache_stats.return_value = {"size": 5}
        mock_embedding.return_value = mock_embedding_client

        pipeline = RAGPipeline()
        stats = pipeline.get_rag_stats()

        assert stats["posts"] == 10
        assert "embedding_cache_size" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
