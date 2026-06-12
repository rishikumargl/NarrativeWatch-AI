"""Tests for research and RAG agents."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.research_agent import ResearchAgent, ResearchFinding
from src.agents.rag_agent import RAGAgent, RAGContext


class TestResearchAgent:
    """Test research agent."""

    @patch("src.agents.research_agent.TavilyAPI")
    @patch("src.agents.research_agent.LLMClient")
    def test_initialization(self, mock_llm, mock_tavily):
        """Test research agent initialization."""
        agent = ResearchAgent()
        assert agent.tavily is not None
        assert agent.llm is not None

    @patch("src.agents.research_agent.TavilyAPI")
    @patch("src.agents.research_agent.LLMClient")
    def test_research_narrative(self, mock_llm, mock_tavily):
        """Test researching a narrative."""
        # Setup mocks
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.search.return_value = [
            {
                "source": "https://bbc.com/article",
                "snippet": "Test evidence",
                "date": "2024-01-01",
            }
        ]
        mock_tavily.return_value = mock_tavily_instance

        mock_llm_instance = MagicMock()
        mock_llm_instance.generate.return_value = "Test summary"
        mock_llm.return_value = mock_llm_instance

        agent = ResearchAgent()
        report = agent.research_narrative(
            narrative_theme="Climate change",
            hashtags=["#climate"],
        )

        assert report.narrative_theme == "Climate change"
        assert len(report.findings) > 0
        assert report.summary is not None

    @patch("src.agents.research_agent.TavilyAPI")
    @patch("src.agents.research_agent.LLMClient")
    def test_verify_claim(self, mock_llm, mock_tavily):
        """Test verifying a claim."""
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.verify_claim.return_value = True
        mock_tavily_instance.search.return_value = [
            {
                "source": "https://example.com",
                "snippet": "Evidence",
                "date": "2024-01-01",
            }
        ]
        mock_tavily.return_value = mock_tavily_instance

        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        agent = ResearchAgent()
        result = agent.verify_claim(claim="The Earth is round")

        assert result["claim"] == "The Earth is round"
        assert "verified" in result
        assert "confidence" in result

    @patch("src.agents.research_agent.TavilyAPI")
    @patch("src.agents.research_agent.LLMClient")
    def test_analyze_hashtag_trends(self, mock_llm, mock_tavily):
        """Test analyzing hashtag trends."""
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.get_trending_content.return_value = {
            "volume": 1000,
            "sentiment": "positive",
            "related_themes": ["nature", "science"],
        }
        mock_tavily.return_value = mock_tavily_instance

        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        agent = ResearchAgent()
        result = agent.analyze_hashtag_trends(hashtags=["#climate", "#environment"])

        assert "trends" in result
        assert "#climate" in result["hashtags"]

    @patch("src.agents.research_agent.TavilyAPI")
    @patch("src.agents.research_agent.LLMClient")
    def test_get_context_about_page(self, mock_llm, mock_tavily):
        """Test getting context about a page."""
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.search.return_value = [
            {
                "source": "https://example.com",
                "snippet": "Page context",
                "date": "2024-01-01",
            }
        ]
        mock_tavily.return_value = mock_tavily_instance

        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        agent = ResearchAgent()
        context = agent.get_context_about_page(
            username="testuser",
            biography="Test bio",
        )

        assert context["username"] == "testuser"
        assert "search_results" in context


class TestRAGAgent:
    """Test RAG agent."""

    @patch("src.agents.rag_agent.get_rag_pipeline")
    @patch("src.agents.rag_agent.ResearchAgent")
    @patch("src.agents.rag_agent.LLMClient")
    def test_initialization(self, mock_llm, mock_research, mock_pipeline):
        """Test RAG agent initialization."""
        agent = RAGAgent()
        assert agent.pipeline is not None
        assert agent.research is not None
        assert agent.llm is not None

    @patch("src.agents.rag_agent.get_rag_pipeline")
    @patch("src.agents.rag_agent.ResearchAgent")
    @patch("src.agents.rag_agent.LLMClient")
    def test_analyze_post(self, mock_llm, mock_research, mock_pipeline):
        """Test analyzing a post."""
        # Setup mocks
        mock_pipeline_instance = MagicMock()
        mock_embedding_client = MagicMock()
        mock_embedding_client.embed_instagram_post.return_value = [0.1] * 1536
        mock_embedding_client.similarity.return_value = 0.8
        mock_pipeline_instance.embedding_client = mock_embedding_client
        mock_pipeline_instance.search_similar_posts.return_value = [
            {
                "post_id": "123",
                "caption": "Similar post",
                "similarity": 0.85,
            }
        ]
        mock_pipeline_instance.search_similar_pages.return_value = []
        mock_pipeline_instance.search_bias_patterns.return_value = []
        mock_pipeline.return_value = mock_pipeline_instance

        mock_research_instance = MagicMock()
        mock_research.return_value = mock_research_instance

        mock_llm_instance = MagicMock()
        mock_llm_instance.generate.return_value = "Test analysis"
        mock_llm.return_value = mock_llm_instance

        agent = RAGAgent()
        analysis = agent.analyze_post(
            post_id="123",
            caption="Test caption",
            hashtags=["#test"],
        )

        assert analysis.query is not None
        assert len(analysis.insights) > 0
        assert len(analysis.recommendations) > 0
        assert analysis.confidence_score > 0

    @patch("src.agents.rag_agent.get_rag_pipeline")
    @patch("src.agents.rag_agent.ResearchAgent")
    @patch("src.agents.rag_agent.LLMClient")
    def test_analyze_page(self, mock_llm, mock_research, mock_pipeline):
        """Test analyzing a page."""
        # Setup mocks
        mock_pipeline_instance = MagicMock()
        mock_embedding_client = MagicMock()
        mock_embedding_client.embed_instagram_page.return_value = [0.1] * 1536
        mock_pipeline_instance.embedding_client = mock_embedding_client
        mock_pipeline_instance.search_similar_posts.return_value = []
        mock_pipeline_instance.search_similar_pages.return_value = [
            {
                "page_id": "page_123",
                "username": "similar_user",
                "similarity": 0.75,
            }
        ]
        mock_pipeline_instance.search_bias_patterns.return_value = []
        mock_pipeline.return_value = mock_pipeline_instance

        mock_research_instance = MagicMock()
        mock_research.return_value = mock_research_instance

        mock_llm_instance = MagicMock()
        mock_llm_instance.generate.return_value = "Page analysis"
        mock_llm.return_value = mock_llm_instance

        agent = RAGAgent()
        analysis = agent.analyze_page(
            page_id="page_123",
            username="testuser",
        )

        assert analysis.query is not None
        assert len(analysis.insights) > 0

    @patch("src.agents.rag_agent.get_rag_pipeline")
    @patch("src.agents.rag_agent.ResearchAgent")
    @patch("src.agents.rag_agent.LLMClient")
    def test_detect_coordinated_behavior(self, mock_llm, mock_research, mock_pipeline):
        """Test detecting coordinated behavior."""
        mock_pipeline_instance = MagicMock()
        mock_embedding_client = MagicMock()
        mock_embedding_client.embed_text.return_value = [0.1] * 1536
        mock_embedding_client.similarity.return_value = 0.8
        mock_pipeline_instance.embedding_client = mock_embedding_client
        mock_pipeline.return_value = mock_pipeline_instance

        mock_research_instance = MagicMock()
        mock_research.return_value = mock_research_instance

        mock_llm_instance = MagicMock()
        mock_llm_instance.generate.return_value = "Coordination analysis"
        mock_llm.return_value = mock_llm_instance

        agent = RAGAgent()
        analysis = agent.detect_coordinated_behavior(
            pages=["user1", "user2", "user3"],
            narratives=["narrative1", "narrative2"],
        )

        assert analysis.query is not None
        assert len(analysis.recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
