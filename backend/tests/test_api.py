"""Tests for API routes."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.routes import (
    AnalysisAPI,
    AnalyzePostRequest,
    AnalyzePageRequest,
)
from src.agents.orchestrator import ContentType, RiskLevel


class TestAnalysisAPI:
    """Test analysis API."""

    @patch("src.api.routes.get_orchestrator")
    def test_initialization(self, mock_orchestrator):
        """Test API initialization."""
        api = AnalysisAPI()
        assert api.orchestrator is not None

    @patch("src.api.routes.get_orchestrator")
    def test_analyze_post(self, mock_orchestrator):
        """Test analyzing post via API."""
        # Setup mocks
        mock_orchestrator_instance = MagicMock()
        mock_analysis = MagicMock()
        mock_analysis.content_id = "123"
        mock_analysis.content_type = ContentType.POST
        mock_analysis.analysis_timestamp = "2024-01-01T00:00:00"
        mock_analysis.rag_analysis = "Test analysis"
        mock_analysis.similar_content_count = 5
        mock_analysis.coordination_signals = ["signal1"]
        mock_analysis.research_summary = "Test summary"
        mock_analysis.credibility_assessment = "HIGH_CREDIBILITY"
        mock_analysis.bias_result = None
        mock_analysis.bot_result = None
        mock_analysis.misinformation_result = None
        mock_analysis.risk_level = RiskLevel.MEDIUM
        mock_analysis.risk_score = 0.5
        mock_analysis.final_recommendations = ["rec1", "rec2"]
        mock_orchestrator_instance.analyze_post.return_value = mock_analysis
        mock_orchestrator.return_value = mock_orchestrator_instance

        api = AnalysisAPI()
        request = AnalyzePostRequest(
            post_id="123",
            page_username="testuser",
            caption="Test caption",
            hashtags=["#test"],
        )

        response = api.analyze_post(request)

        assert response.content_id == "123"
        assert response.content_type == "post"
        assert response.risk_level == "medium"

    @patch("src.api.routes.get_orchestrator")
    def test_analyze_page(self, mock_orchestrator):
        """Test analyzing page via API."""
        mock_orchestrator_instance = MagicMock()
        mock_analysis = MagicMock()
        mock_analysis.content_id = "page_123"
        mock_analysis.content_type = ContentType.PAGE
        mock_analysis.analysis_timestamp = "2024-01-01T00:00:00"
        mock_analysis.rag_analysis = "Page analysis"
        mock_analysis.similar_content_count = 3
        mock_analysis.coordination_signals = []
        mock_analysis.research_summary = None
        mock_analysis.credibility_assessment = None
        mock_analysis.bias_result = None
        mock_analysis.bot_result = None
        mock_analysis.misinformation_result = None
        mock_analysis.risk_level = RiskLevel.LOW
        mock_analysis.risk_score = 0.2
        mock_analysis.final_recommendations = ["Monitor"]
        mock_orchestrator_instance.analyze_page.return_value = mock_analysis
        mock_orchestrator.return_value = mock_orchestrator_instance

        api = AnalysisAPI()
        request = AnalyzePageRequest(
            page_id="page_123",
            username="testuser",
        )

        response = api.analyze_page(request)

        assert response.content_id == "page_123"
        assert response.content_type == "page"
        assert response.risk_level == "low"

    @patch("src.api.routes.get_orchestrator")
    def test_get_rag_stats(self, mock_orchestrator):
        """Test getting RAG statistics."""
        mock_orchestrator_instance = MagicMock()
        mock_pipeline = MagicMock()
        mock_pipeline.get_rag_stats.return_value = {
            "posts": 100,
            "pages": 50,
            "embedding_cache_size": 25,
        }
        mock_orchestrator_instance.pipeline = mock_pipeline
        mock_orchestrator.return_value = mock_orchestrator_instance

        api = AnalysisAPI()
        stats = api.get_rag_stats()

        assert stats["posts"] == 100
        assert stats["pages"] == 50

    @patch("src.api.routes.get_orchestrator")
    def test_health_check(self, mock_orchestrator):
        """Test health check."""
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.bias_agent = None
        mock_orchestrator_instance.bot_agent = None
        mock_orchestrator_instance.misinformation_agent = None
        mock_orchestrator.return_value = mock_orchestrator_instance

        api = AnalysisAPI()
        health = api.health_check()

        assert health["status"] == "healthy"
        assert "components" in health
        assert health["components"]["orchestrator"] == "ready"
        assert health["components"]["bias_agent"] == "pending"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
