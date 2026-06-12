"""Unit tests for ContentAnalyzerAgent."""

import pytest
from datetime import datetime
from src.agents.content_analyzer import ContentAnalyzerAgent


class TestContentAnalyzerAgent:
    """Test ContentAnalyzerAgent class."""

    @pytest.fixture
    def agent(self):
        """Create ContentAnalyzerAgent instance."""
        return ContentAnalyzerAgent()

    @pytest.fixture
    def sample_instagram_data(self):
        """Create sample Instagram data."""
        return {
            "caption": "Check out this amazing new product! #trending #innovation #future",
            "hashtags": ["#trending", "#innovation", "#future", "#trending"],
            "comments": [
                "This looks great!",
                "I love this",
                "Amazing product",
                "Where can I buy?",
            ],
            "posting_time": "2024-06-12T14:30:00",
            "engagement": {
                "likes": 1500,
                "comments": 45,
                "shares": 120,
                "engagement_rate": 0.08,
            }
        }

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "Content Analyzer"
        assert agent.text_processor is not None

    def test_validate_input_valid(self, agent, sample_instagram_data):
        """Test input validation with valid data."""
        assert agent.validate_input(sample_instagram_data) is True

    def test_validate_input_missing_caption(self, agent):
        """Test input validation with missing caption."""
        data = {"hashtags": ["#test"]}
        assert agent.validate_input(data) is False

    def test_validate_input_invalid_type(self, agent):
        """Test input validation with invalid type."""
        assert agent.validate_input("invalid") is False
        assert agent.validate_input(None) is False

    def test_run_success(self, agent, sample_instagram_data):
        """Test successful analysis run."""
        result = agent.run(sample_instagram_data)
        assert result["status"] == "success"
        assert "analysis" in result
        assert "timestamp" in result

    def test_run_error_handling(self, agent):
        """Test error handling."""
        result = agent.run({"caption": ""})
        # Should handle gracefully
        assert "status" in result

    def test_emotional_language_analysis(self, agent, sample_instagram_data):
        """Test emotional language analysis."""
        result = agent.run(sample_instagram_data)
        analysis = result["analysis"]
        emotional = analysis["emotional_language"]

        assert "sentiment" in emotional
        assert "subjectivity" in emotional
        assert "emotional_intensity" in emotional
        assert "overall_tone" in emotional

    def test_sentiment_classification(self, agent):
        """Test sentiment classification."""
        positive_data = {
            "caption": "I absolutely love this! Amazing! Incredible!",
            "hashtags": [],
            "comments": [],
            "posting_time": None,
            "engagement": {}
        }
        result = agent.run(positive_data)
        sentiment = result["analysis"]["emotional_language"]["sentiment"]
        assert sentiment["polarity"] > 0
        assert sentiment["classification"] == "positive"

    def test_narrative_themes_detection(self, agent):
        """Test narrative theme detection."""
        political_data = {
            "caption": "Vote for freedom and liberty! #election #campaign",
            "hashtags": ["#election", "#campaign"],
            "comments": ["Vote now!", "Political message"],
            "posting_time": None,
            "engagement": {}
        }
        result = agent.run(political_data)
        themes = result["analysis"]["narrative_themes"]
        assert "political" in themes

    def test_hashtag_analysis(self, agent, sample_instagram_data):
        """Test hashtag analysis."""
        result = agent.run(sample_instagram_data)
        hashtag_analysis = result["analysis"]["hashtag_patterns"]

        assert hashtag_analysis["total_hashtags"] == 4
        assert hashtag_analysis["unique_hashtags"] == 3
        assert "#trending" in hashtag_analysis["hashtag_frequency"]
        assert hashtag_analysis["hashtag_frequency"]["#trending"] == 2

    def test_hashtag_patterns_empty(self, agent):
        """Test hashtag analysis with no hashtags."""
        data = {
            "caption": "No hashtags here",
            "hashtags": [],
            "comments": [],
            "posting_time": None,
            "engagement": {}
        }
        result = agent.run(data)
        hashtag_analysis = result["analysis"]["hashtag_patterns"]
        assert hashtag_analysis["total_hashtags"] == 0

    def test_posting_pattern_analysis(self, agent, sample_instagram_data):
        """Test posting pattern analysis."""
        result = agent.run(sample_instagram_data)
        pattern = result["analysis"]["posting_pattern"]

        assert "frequency" in pattern
        assert "consistency" in pattern
        assert "timing_pattern" in pattern
        assert pattern["timing_pattern"] == "afternoon"

    def test_engagement_metrics_analysis(self, agent, sample_instagram_data):
        """Test engagement metrics analysis."""
        result = agent.run(sample_instagram_data)
        engagement = result["analysis"]["engagement_metrics"]

        assert engagement["likes"] == 1500
        assert engagement["comments"] == 45
        assert engagement["shares"] == 120
        assert engagement["engagement_rate"] == 0.08
        assert engagement["engagement_quality"] == "high"

    def test_text_patterns_analysis(self, agent, sample_instagram_data):
        """Test text pattern analysis."""
        result = agent.run(sample_instagram_data)
        patterns = result["analysis"]["text_patterns"]

        assert "language_features" in patterns
        assert "named_entities" in patterns
        assert "readability" in patterns
        assert "word_frequency" in patterns

    def test_engagement_quality_assessment(self, agent):
        """Test engagement quality assessment."""
        high_engagement = {
            "caption": "Test",
            "hashtags": [],
            "comments": [],
            "posting_time": None,
            "engagement": {"engagement_rate": 0.12}
        }
        result = agent.run(high_engagement)
        quality = result["analysis"]["engagement_metrics"]["engagement_quality"]
        assert quality == "high"

        low_engagement = {
            "caption": "Test",
            "hashtags": [],
            "comments": [],
            "posting_time": None,
            "engagement": {"engagement_rate": 0.01}
        }
        result = agent.run(low_engagement)
        quality = result["analysis"]["engagement_metrics"]["engagement_quality"]
        assert quality == "low"


class TestContentAnalyzerEdgeCases:
    """Test edge cases for ContentAnalyzerAgent."""

    @pytest.fixture
    def agent(self):
        """Create ContentAnalyzerAgent instance."""
        return ContentAnalyzerAgent()

    def test_empty_caption(self, agent):
        """Test with empty caption."""
        data = {
            "caption": "",
            "hashtags": [],
            "comments": [],
            "posting_time": None,
            "engagement": {}
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_very_long_caption(self, agent):
        """Test with very long caption."""
        long_text = "word " * 5000
        data = {
            "caption": long_text,
            "hashtags": [],
            "comments": [],
            "posting_time": None,
            "engagement": {}
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_many_comments(self, agent):
        """Test with many comments."""
        data = {
            "caption": "Test",
            "hashtags": [],
            "comments": ["Comment " + str(i) for i in range(1000)],
            "posting_time": None,
            "engagement": {}
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_special_characters(self, agent):
        """Test with special characters in caption."""
        data = {
            "caption": "Test!@#$%^&*()_+-=[]{}|;:',.<>?/",
            "hashtags": [],
            "comments": [],
            "posting_time": None,
            "engagement": {}
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_unicode_content(self, agent):
        """Test with unicode content."""
        data = {
            "caption": "Hello 世界 مرحبا мир",
            "hashtags": ["#worldwideweb"],
            "comments": ["Nice post!"],
            "posting_time": None,
            "engagement": {}
        }
        result = agent.run(data)
        assert result["status"] == "success"
