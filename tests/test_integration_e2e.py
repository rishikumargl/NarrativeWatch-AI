"""End-to-end integration tests for complete analysis pipeline."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.orchestrator import (
    get_orchestrator,
    ContentType,
    RiskLevel,
)
from src.agents.example_agents import (
    ExampleBiasAgent,
    ExampleBotAgent,
    ExampleMisinformationAgent,
)
from src.api.routes import get_analysis_api, AnalyzePostRequest


class TestE2EPostAnalysis:
    """End-to-end tests for post analysis pipeline."""

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_full_post_analysis_with_all_agents(self, mock_pipeline, mock_rag, mock_research):
        """Test complete post analysis with all agents."""
        # Setup mocks for RAG agent
        mock_rag_instance = MagicMock()
        mock_rag_result = MagicMock()
        mock_rag_result.analysis = "Found similar posts with bias indicators"
        mock_rag_result.confidence_score = 0.85
        mock_rag_result.insights = ["High similarity to banned posts", "Coordination signals detected"]
        mock_rag_result.recommendations = ["Flag for review"]
        mock_rag_result.context.similar_posts = [
            {"post_id": "456", "similarity": 0.87},
            {"post_id": "789", "similarity": 0.82},
        ]
        mock_rag_result.context.similar_pages = []
        mock_rag_instance.analyze_post.return_value = mock_rag_result
        mock_rag.return_value = mock_rag_instance

        # Setup mocks for research agent
        mock_research_instance = MagicMock()
        mock_research_result = MagicMock()
        mock_research_result.summary = "Claim contradicted by 3 reputable sources"
        mock_research_result.credibility_assessment = "LOW_CREDIBILITY"
        mock_research_instance.research_narrative.return_value = mock_research_result
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        # Get orchestrator and register example agents
        orchestrator = get_orchestrator()
        bias_agent = ExampleBiasAgent()
        bot_agent = ExampleBotAgent()
        misinformation_agent = ExampleMisinformationAgent()

        orchestrator.register_bias_agent(bias_agent)
        orchestrator.register_bot_agent(bot_agent)
        orchestrator.register_misinformation_agent(misinformation_agent)

        # Analyze post
        analysis = orchestrator.analyze_post(
            post_id="test_123",
            page_username="suspicious_account",
            caption="Doctors recommend this miracle cure",
            hashtags=["#health", "#proven"],
            likes=1000,
            comments=10,
        )

        # Verify results
        assert analysis.content_id == "test_123"
        assert analysis.content_type == ContentType.POST

        # Should have all agent results
        assert analysis.bias_result is not None
        assert analysis.bot_result is not None
        assert analysis.misinformation_result is not None

        # Verify bias detection
        assert analysis.bias_result.bias_detected == False  # "doctors" not in pattern

        # Verify bot detection
        assert analysis.bot_result.bot_detected == True  # Low comment ratio
        assert analysis.bot_result.bot_score > 0.3

        # Verify misinformation detection
        assert analysis.misinformation_result.misleading_content == True
        assert "miracle" in " ".join(analysis.misinformation_result.contradictions).lower()

        # Verify risk aggregation
        assert analysis.risk_level in [
            RiskLevel.CRITICAL,
            RiskLevel.HIGH,
            RiskLevel.MEDIUM,
        ]
        assert analysis.risk_score > 0.4

        # Verify recommendations
        assert len(analysis.final_recommendations) > 0

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_post_analysis_low_risk(self, mock_pipeline, mock_rag, mock_research):
        """Test post analysis with low-risk content."""
        # Setup mocks
        mock_rag_instance = MagicMock()
        mock_rag_result = MagicMock()
        mock_rag_result.analysis = "Clean content"
        mock_rag_result.confidence_score = 0.9
        mock_rag_result.insights = []
        mock_rag_result.recommendations = []
        mock_rag_result.context.similar_posts = []
        mock_rag_result.context.similar_pages = []
        mock_rag_instance.analyze_post.return_value = mock_rag_result
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research_result = MagicMock()
        mock_research_result.summary = "Claim verified"
        mock_research_result.credibility_assessment = "HIGH_CREDIBILITY"
        mock_research_instance.research_narrative.return_value = mock_research_result
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = get_orchestrator()
        orchestrator.register_bias_agent(ExampleBiasAgent())
        orchestrator.register_bot_agent(ExampleBotAgent())
        orchestrator.register_misinformation_agent(ExampleMisinformationAgent())

        analysis = orchestrator.analyze_post(
            post_id="clean_123",
            page_username="trusted_account",
            caption="Beautiful sunset photo",
            hashtags=["#nature", "#photography"],
            likes=500,
            comments=50,  # Good engagement ratio
        )

        # Verify low risk
        assert analysis.risk_level in [RiskLevel.LOW, RiskLevel.NONE]

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_post_analysis_with_api(self, mock_pipeline, mock_rag, mock_research):
        """Test post analysis through API."""
        # Setup mocks
        mock_rag_instance = MagicMock()
        mock_rag_result = MagicMock()
        mock_rag_result.analysis = "Analysis complete"
        mock_rag_result.confidence_score = 0.8
        mock_rag_result.insights = ["Finding 1"]
        mock_rag_result.recommendations = ["Rec 1"]
        mock_rag_result.context.similar_posts = []
        mock_rag_result.context.similar_pages = []
        mock_rag_instance.analyze_post.return_value = mock_rag_result
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research_instance.research_narrative.return_value = None
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        # Use API
        api = get_analysis_api()
        request = AnalyzePostRequest(
            post_id="api_123",
            page_username="test_user",
            caption="Test content",
            hashtags=["#test"],
        )

        response = api.analyze_post(request)

        assert response.content_id == "api_123"
        assert response.content_type == "post"
        assert response.risk_level in ["critical", "high", "medium", "low", "none"]


class TestE2EPageAnalysis:
    """End-to-end tests for page analysis pipeline."""

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_full_page_analysis_with_agents(self, mock_pipeline, mock_rag, mock_research):
        """Test complete page analysis with all agents."""
        # Setup mocks
        mock_rag_instance = MagicMock()
        mock_rag_result = MagicMock()
        mock_rag_result.analysis = "Page analysis"
        mock_rag_result.confidence_score = 0.8
        mock_rag_result.insights = []
        mock_rag_result.recommendations = []
        mock_rag_result.context.similar_posts = []
        mock_rag_result.context.similar_pages = [
            {"page_id": "page_456", "similarity": 0.85}
        ]
        mock_rag_instance.analyze_page.return_value = mock_rag_result
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research_instance.get_context_about_page.return_value = {}
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = get_orchestrator()
        orchestrator.register_bot_agent(ExampleBotAgent())

        analysis = orchestrator.analyze_page(
            page_id="page_123",
            username="suspicious_page",
            biography="Buy followers here",
            followers=50000,
        )

        assert analysis.content_id == "page_123"
        assert analysis.content_type == ContentType.PAGE
        assert analysis.bot_result is not None


class TestE2EAgentIntegration:
    """Tests for agent integration."""

    def test_bias_agent_integration(self):
        """Test bias agent integration."""
        bias_agent = ExampleBiasAgent()

        result = bias_agent.detect_bias(
            caption="A woman should cook and a man should work",
            hashtags=["#traditional"],
        )

        assert result.bias_detected == True
        assert "gender" in result.bias_categories
        assert result.bias_score > 0.3

    def test_bot_agent_integration(self):
        """Test bot agent integration."""
        bot_agent = ExampleBotAgent()

        # Suspicious engagement
        result = bot_agent.detect_bot(
            page="bot_account",
            engagement=(5000, 10),  # Very low comment ratio
        )

        assert result.bot_detected == True
        assert result.bot_score > 0.3

    def test_misinformation_agent_integration(self):
        """Test misinformation agent integration."""
        misinformation_agent = ExampleMisinformationAgent()

        result = misinformation_agent.detect_misinformation(
            caption="This miracle cure is proven 100% effective",
            hashtags=["#health"],
        )

        assert result.misleading_content == True
        assert result.claim_accuracy < 0.7
        assert len(result.contradictions) > 0

    def test_all_agents_with_orchestrator(self):
        """Test all agents working together with orchestrator."""
        with patch("src.agents.orchestrator.ResearchAgent"):
            with patch("src.agents.orchestrator.RAGAgent"):
                with patch("src.agents.orchestrator.get_rag_pipeline"):
                    orchestrator = get_orchestrator()

                    # Register example agents
                    bias_agent = ExampleBiasAgent()
                    bot_agent = ExampleBotAgent()
                    misinformation_agent = ExampleMisinformationAgent()

                    orchestrator.register_bias_agent(bias_agent)
                    orchestrator.register_bot_agent(bot_agent)
                    orchestrator.register_misinformation_agent(
                        misinformation_agent
                    )

                    # Verify registration
                    assert orchestrator.bias_agent == bias_agent
                    assert orchestrator.bot_agent == bot_agent
                    assert (
                        orchestrator.misinformation_agent == misinformation_agent
                    )


class TestE2EDataFlow:
    """Tests for complete data flow."""

    @patch("src.agents.orchestrator.ResearchAgent")
    @patch("src.agents.orchestrator.RAGAgent")
    @patch("src.agents.orchestrator.get_rag_pipeline")
    def test_suspicious_post_detection(self, mock_pipeline, mock_rag, mock_research):
        """Test detection of suspicious post combining all agents."""
        # Setup
        mock_rag_instance = MagicMock()
        mock_rag_result = MagicMock()
        mock_rag_result.analysis = "Coordinates with known spam accounts"
        mock_rag_result.confidence_score = 0.9
        mock_rag_result.insights = ["Coordination detected"]
        mock_rag_result.recommendations = ["Flag account"]
        mock_rag_result.context.similar_posts = [
            {"post_id": "spam_1"},
            {"post_id": "spam_2"},
        ]
        mock_rag_result.context.similar_pages = []
        mock_rag_instance.analyze_post.return_value = mock_rag_result
        mock_rag.return_value = mock_rag_instance

        mock_research_instance = MagicMock()
        mock_research_instance.research_narrative.return_value = None
        mock_research.return_value = mock_research_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        orchestrator = get_orchestrator()
        orchestrator.register_bias_agent(ExampleBiasAgent())
        orchestrator.register_bot_agent(ExampleBotAgent())
        orchestrator.register_misinformation_agent(ExampleMisinformationAgent())

        # Analyze suspicious content
        analysis = orchestrator.analyze_post(
            post_id="sus_123",
            page_username="bot_network_member",
            caption="Buy followers cheap 100 percent real",
            hashtags=["#growth", "#followers"],
            likes=5000,
            comments=5,
        )

        # Verify detection
        assert analysis.bot_result.bot_detected == True
        assert analysis.misinformation_result.misleading_content == True
        assert analysis.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]
        assert len(analysis.final_recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
