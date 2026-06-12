"""Tests for orchestrator."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.orchestrator import (
    Orchestrator,
    get_orchestrator,
    RiskLevel,
    ContentType,
    BiasAnalysisResult,
)


class TestOrchestrator:
    """Test orchestrator."""

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_initialization(self, mock_pipeline, mock_rag, mock_research):
        """Test orchestrator initialization."""
        orchestrator = Orchestrator()
        assert orchestrator.research_agent is not None
        assert orchestrator.rag_agent is not None
        assert orchestrator.pipeline is not None

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_analyze_post(self, mock_pipeline, mock_rag, mock_research):
        """Test analyzing a post."""
        # Setup mocks
        mock_rag_instance = MagicMock()
        mock_rag_result = MagicMock()
        mock_rag_result.analysis = "Test RAG analysis"
        mock_rag_result.confidence_score = 0.85
        mock_rag_result.insights = ["insight1"]
        mock_rag_result.recommendations = ["rec1"]
        mock_rag_result.context.similar_posts = [{"post_id": "123"}]
        mock_rag_instance.analyze_post.return_value = mock_rag_result
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research_result = MagicMock()
        mock_research_result.summary = "Test research summary"
        mock_research_result.credibility_assessment = "HIGH_CREDIBILITY"
        mock_research_instance.research_narrative.return_value = mock_research_result
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = Orchestrator()
        analysis = orchestrator.analyze_post(
            post_id="123",
            page_username="testuser",
            caption="Test caption",
            hashtags=["#test"],
        )

        assert analysis.content_id == "123"
        assert analysis.content_type == ContentType.POST
        assert len(analysis.rag_analysis) > 0
        assert analysis.risk_level is not None

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_analyze_page(self, mock_pipeline, mock_rag, mock_research):
        """Test analyzing a page."""
        mock_rag_instance = MagicMock()
        mock_rag_result = MagicMock()
        mock_rag_result.analysis = "Test page analysis"
        mock_rag_result.confidence_score = 0.8
        mock_rag_result.insights = []
        mock_rag_result.recommendations = []
        mock_rag_result.context.similar_posts = []
        mock_rag_instance.analyze_page.return_value = mock_rag_result
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research_instance.get_context_about_page.return_value = {}
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = Orchestrator()
        analysis = orchestrator.analyze_page(
            page_id="page_123",
            username="testuser",
        )

        assert analysis.content_id == "page_123"
        assert analysis.content_type == ContentType.PAGE

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_register_bias_agent(self, mock_pipeline, mock_rag, mock_research):
        """Test registering bias agent."""
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = Orchestrator()
        mock_bias_agent = MagicMock()

        orchestrator.register_bias_agent(mock_bias_agent)
        assert orchestrator.bias_agent == mock_bias_agent

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_register_bot_agent(self, mock_pipeline, mock_rag, mock_research):
        """Test registering bot agent."""
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = Orchestrator()
        mock_bot_agent = MagicMock()

        orchestrator.register_bot_agent(mock_bot_agent)
        assert orchestrator.bot_agent == mock_bot_agent

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_calculate_risk_level_critical(self, mock_pipeline, mock_rag, mock_research):
        """Test calculating critical risk level."""
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = Orchestrator()

        bias_result = BiasAnalysisResult(
            bias_detected=True,
            bias_categories=["gender"],
            bias_score=0.9,
            indicators=["ind1"],
            description="High bias detected",
        )

        risk_level, risk_score = orchestrator._calculate_risk_level(
            bias_result=bias_result,
            bot_result=None,
            misinformation_result=None,
            rag_confidence=0.8,
        )

        assert risk_level == RiskLevel.CRITICAL
        assert risk_score >= 0.8

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_calculate_risk_level_none(self, mock_pipeline, mock_rag, mock_research):
        """Test calculating no risk level."""
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = Orchestrator()

        risk_level, risk_score = orchestrator._calculate_risk_level(
            bias_result=None,
            bot_result=None,
            misinformation_result=None,
            rag_confidence=0.8,
        )

        assert risk_level == RiskLevel.NONE
        assert risk_score == 0.0

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_generate_recommendations(self, mock_pipeline, mock_rag, mock_research):
        """Test generating recommendations."""
        mock_rag_instance = MagicMock()
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = Orchestrator()

        bias_result = BiasAnalysisResult(
            bias_detected=True,
            bias_categories=["gender"],
            bias_score=0.9,
            indicators=["ind1"],
            description="Bias detected",
        )

        recommendations = orchestrator._generate_recommendations(
            bias_result=bias_result,
            bot_result=None,
            misinformation_result=None,
            risk_level=RiskLevel.CRITICAL,
            rag_recommendations=["RAG rec1"],
        )

        assert len(recommendations) > 0
        assert any("bias" in rec.lower() for rec in recommendations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
