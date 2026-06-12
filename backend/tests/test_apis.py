"""Tests for external API clients."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.apis.tavily_api import TavilyAPI
from src.apis.instagram_api import InstagramAPI
from src.apis.llm_client import LLMClient


class TestTavilyAPI:
    """Test Tavily Search API wrapper."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    def test_initialization(self):
        """Test TavilyAPI initialization."""
        api = TavilyAPI()
        assert api.api_key == "test_key"
        assert api.base_url == "https://api.tavily.com/search"

    def test_missing_api_key(self):
        """Test error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TAVILY_API_KEY"):
                TavilyAPI()

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("requests.Session.post")
    def test_search(self, mock_post):
        """Test search functionality."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"title": "Test", "url": "http://test.com", "snippet": "Test snippet"}
            ],
            "answer": "Test answer",
        }
        mock_post.return_value = mock_response

        api = TavilyAPI()
        result = api.search("test query", max_results=5)

        assert "results" in result
        assert "answer" in result
        assert result["query"] == "test query"

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("requests.Session.post")
    def test_verify_claim(self, mock_post):
        """Test claim verification."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"title": "Fact Check", "url": "http://snopes.com", "snippet": "Claim is false"}
            ],
            "answer": "This claim is false",
        }
        mock_post.return_value = mock_response

        api = TavilyAPI()
        result = api.verify_claim("test claim")

        assert "claim" in result
        assert "sources" in result
        assert result["verified"] == True

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("requests.Session.post")
    def test_health_check(self, mock_post):
        """Test API health check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = TavilyAPI()
        is_healthy = api.check_health()

        assert is_healthy == True


class TestInstagramAPI:
    """Test Instagram Graph API wrapper."""

    @patch.dict(os.environ, {"INSTAGRAM_ACCESS_TOKEN": "test_token"})
    def test_initialization(self):
        """Test InstagramAPI initialization."""
        api = InstagramAPI()
        assert api.access_token == "test_token"
        assert api.base_url == "https://graph.instagram.com/v18.0"

    def test_missing_access_token(self):
        """Test error when token is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="INSTAGRAM_ACCESS_TOKEN"):
                InstagramAPI()

    @patch.dict(os.environ, {"INSTAGRAM_ACCESS_TOKEN": "test_token"})
    @patch("requests.Session.request")
    def test_get_page(self, mock_request):
        """Test getting page info."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "123",
            "username": "testuser",
            "follower_count": 1000,
        }
        mock_request.return_value = mock_response

        api = InstagramAPI()
        result = api.get_page("testuser")

        assert result["username"] == "testuser"
        assert result["follower_count"] == 1000

    @patch.dict(os.environ, {"INSTAGRAM_ACCESS_TOKEN": "test_token"})
    @patch("requests.Session.request")
    def test_get_page_posts(self, mock_request):
        """Test getting page posts."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "123",
                    "caption": "Test post",
                    "like_count": 100,
                }
            ]
        }
        mock_request.return_value = mock_response

        api = InstagramAPI()
        result = api.get_page_posts("testuser", limit=10)

        assert "data" in result

    @patch.dict(os.environ, {"INSTAGRAM_ACCESS_TOKEN": "test_token"})
    @patch("requests.Session.head")
    def test_health_check(self, mock_head):
        """Test API health check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        api = InstagramAPI()
        is_healthy = api.check_health()

        assert is_healthy == True


class TestLLMClient:
    """Test Vertex AI LLM client."""

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.generative_models.GenerativeModel")
    def test_initialization(self, mock_model, mock_init):
        """Test LLM client initialization."""
        client = LLMClient()
        assert client.project_id == "test_project"
        assert client.model_name == "gemini-2.5-pro"
        assert client.temperature == 0.7
        assert client.max_tokens == 2048
        mock_init.assert_called_once()

    def test_missing_project_id(self):
        """Test error when project ID is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="VERTEX_AI_PROJECT_ID"):
                LLMClient()

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.generative_models.GenerativeModel")
    def test_generate(self, mock_model_class, mock_init):
        """Test text generation."""
        mock_response = MagicMock()
        mock_response.text = "Generated text"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        client = LLMClient()
        result = client.generate("Test prompt")

        assert result == "Generated text"
        mock_model.generate_content.assert_called_once()

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.generative_models.GenerativeModel")
    def test_classify(self, mock_model_class, mock_init):
        """Test text classification."""
        mock_response = MagicMock()
        mock_response.text = "positive"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        client = LLMClient()
        result = client.classify("I love this!", ["positive", "negative"])

        assert "classification" in result
        assert result["labels"] == ["positive", "negative"]

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.generative_models.GenerativeModel")
    def test_summarize(self, mock_model_class, mock_init):
        """Test text summarization."""
        mock_response = MagicMock()
        mock_response.text = "This is a summary"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        client = LLMClient()
        result = client.summarize("Long text about something important...")

        assert isinstance(result, str)

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.generative_models.GenerativeModel")
    def test_health_check(self, mock_model_class, mock_init):
        """Test LLM health check."""
        mock_response = MagicMock()
        mock_response.text = "OK"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        client = LLMClient()
        is_healthy = client.check_health()

        assert is_healthy == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
