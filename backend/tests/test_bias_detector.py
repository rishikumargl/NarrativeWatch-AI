"""Unit tests for BiasDetectorAgent."""

import pytest
from src.agents.bias_detector import BiasDetectorAgent


class TestBiasDetectorAgent:
    """Test BiasDetectorAgent class."""

    @pytest.fixture
    def agent(self):
        """Create BiasDetectorAgent instance."""
        return BiasDetectorAgent()

    @pytest.fixture
    def sample_content(self):
        """Create sample content."""
        return {
            "text": "We must protect our borders and preserve traditional values",
            "comments": [
                "Totally agree with this perspective",
                "Strong conservative values"
            ]
        }

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "Bias Detector"
        assert agent.text_processor is not None
        assert agent.political_keywords is not None
        assert agent.gender_keywords is not None
        assert agent.ideology_keywords is not None

    def test_validate_input_valid(self, agent, sample_content):
        """Test input validation with valid data."""
        assert agent.validate_input(sample_content) is True

    def test_validate_input_missing_text(self, agent):
        """Test input validation with missing text."""
        data = {"comments": ["test"]}
        assert agent.validate_input(data) is False

    def test_validate_input_invalid_type(self, agent):
        """Test input validation with invalid type."""
        assert agent.validate_input("invalid") is False
        assert agent.validate_input(None) is False

    def test_run_success(self, agent, sample_content):
        """Test successful analysis run."""
        result = agent.run(sample_content)
        assert result["status"] == "success"
        assert "analysis" in result
        assert "timestamp" in result

    def test_political_bias_detection(self, agent):
        """Test political bias detection."""
        liberal_content = {
            "text": "We need more social justice and equality for all marginalized communities",
            "comments": []
        }
        result = agent.run(liberal_content)
        political = result["analysis"]["political_bias"]

        assert "left_score" in political
        assert "right_score" in political
        assert "center_score" in political
        assert "bias_direction" in political
        assert "confidence" in political
        assert all(0 <= political[key] <= 1 for key in ["left_score", "right_score", "center_score"])

    def test_conservative_bias_detection(self, agent):
        """Test conservative bias detection."""
        conservative_content = {
            "text": "We must protect our borders and preserve traditional values",
            "comments": []
        }
        result = agent.run(conservative_content)
        political = result["analysis"]["political_bias"]
        assert political["right_score"] >= political["left_score"]

    def test_center_bias_detection(self, agent):
        """Test center bias detection."""
        center_content = {
            "text": "We need bipartisan compromise and balanced approaches",
            "comments": []
        }
        result = agent.run(center_content)
        political = result["analysis"]["political_bias"]
        assert "center" in political["bias_direction"] or political["center_score"] > 0

    def test_gender_bias_detection(self, agent):
        """Test gender bias detection."""
        content = {
            "text": "Women are the strongest beings and should lead all organizations",
            "comments": []
        }
        result = agent.run(content)
        gender = result["analysis"]["gender_bias"]

        assert "male_bias" in gender
        assert "female_bias" in gender
        assert "neutral" in gender
        assert "bias_direction" in gender
        assert all(0 <= gender[key] <= 1 for key in ["male_bias", "female_bias", "neutral"])

    def test_ideological_bias_detection(self, agent):
        """Test ideological bias detection."""
        progressive_content = {
            "text": "We need to embrace change and innovation for progress",
            "comments": []
        }
        result = agent.run(progressive_content)
        ideology = result["analysis"]["ideological_bias"]

        assert "progressive_score" in ideology
        assert "conservative_score" in ideology
        assert "moderate_score" in ideology
        assert "ideology_direction" in ideology

    def test_toxicity_detection(self, agent):
        """Test toxicity detection."""
        toxic_content = {
            "text": "I hate this and these people are stupid idiots",
            "comments": []
        }
        result = agent.run(toxic_content)
        toxicity = result["analysis"]["toxicity_score"]
        assert 0 <= toxicity <= 1
        assert toxicity > 0

    def test_non_toxic_content(self, agent):
        """Test non-toxic content."""
        clean_content = {
            "text": "This is a nice day for a picnic",
            "comments": []
        }
        result = agent.run(clean_content)
        toxicity = result["analysis"]["toxicity_score"]
        assert toxicity <= 0.3

    def test_bias_indicators_extraction(self, agent):
        """Test bias indicator extraction."""
        biased_content = {
            "text": "All women should have equal rights and all men need to change",
            "comments": []
        }
        result = agent.run(biased_content)
        indicators = result["analysis"]["bias_indicators"]
        assert len(indicators) > 0
        assert all("phrase" in ind and "type" in ind for ind in indicators)

    def test_overall_bias_score(self, agent):
        """Test overall bias score calculation."""
        content = {
            "text": "Strong conservative values are important",
            "comments": []
        }
        result = agent.run(content)
        overall_score = result["analysis"]["overall_bias_score"]
        assert 0 <= overall_score <= 1

    def test_multiple_biases(self, agent):
        """Test detection of multiple biases."""
        content = {
            "text": "Conservative men should lead while women stay home",
            "comments": []
        }
        result = agent.run(content)
        analysis = result["analysis"]

        # Should detect multiple biases
        assert analysis["political_bias"]["right_score"] > 0
        assert analysis["gender_bias"]["male_bias"] > 0


class TestBiasDetectorEdgeCases:
    """Test edge cases for BiasDetectorAgent."""

    @pytest.fixture
    def agent(self):
        """Create BiasDetectorAgent instance."""
        return BiasDetectorAgent()

    def test_empty_text(self, agent):
        """Test with empty text."""
        data = {"text": "", "comments": []}
        result = agent.run(data)
        assert result["status"] == "success"

    def test_very_long_text(self, agent):
        """Test with very long text."""
        long_text = "word " * 5000
        data = {"text": long_text, "comments": []}
        result = agent.run(data)
        assert result["status"] == "success"

    def test_unicode_content(self, agent):
        """Test with unicode content."""
        data = {
            "text": "Hello 世界 مرحبا мир",
            "comments": []
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_special_characters(self, agent):
        """Test with special characters."""
        data = {
            "text": "!@#$%^&*()_+-=[]{}|;:',.<>?/",
            "comments": []
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_many_comments(self, agent):
        """Test with many comments."""
        data = {
            "text": "Test content",
            "comments": ["Comment " + str(i) for i in range(1000)]
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_neutral_content(self, agent):
        """Test with neutral content."""
        data = {
            "text": "The sky is blue. Water is wet. Grass is green.",
            "comments": []
        }
        result = agent.run(data)
        analysis = result["analysis"]
        # Neutral content should have relatively balanced scores
        political = analysis["political_bias"]
        assert political["center_score"] >= 0
