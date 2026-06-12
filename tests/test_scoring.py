"""Tests for Trust Score Calculator."""

import pytest
from src.utils.scoring import TrustScoreCalculator, ComponentScores


@pytest.fixture
def calculator():
    return TrustScoreCalculator()


@pytest.fixture
def sample_agent_results():
    return {
        "bot_detector": {"bot_probability": 0.3},
        "research_agent": {"fact_checks": ["FALSE", "TRUE", "TRUE"]},
        "bias_detector": {"political_bias": 0.4},
        "content_analyzer": {"emotional_score": 0.5},
        "campaign_detector": {"campaign_confidence": 0.3}
    }


@pytest.fixture
def high_risk_results():
    return {
        "bot_detector": {"bot_probability": 0.9},
        "research_agent": {"fact_checks": ["FALSE", "FALSE", "FALSE"]},
        "bias_detector": {"political_bias": 0.9},
        "content_analyzer": {"emotional_score": 0.9},
        "campaign_detector": {"campaign_confidence": 0.9}
    }


class TestComponentScores:
    """Test ComponentScores dataclass."""

    def test_valid_scores(self):
        """Test creating valid component scores."""
        scores = ComponentScores(
            authenticity=80,
            truthfulness=70,
            bias=50,
            manipulation=60,
            campaign_activity=40
        )

        assert scores.authenticity == 80
        assert scores.truthfulness == 70

    def test_invalid_authenticity_high(self):
        """Test that scores > 100 are rejected."""
        with pytest.raises(ValueError):
            ComponentScores(
                authenticity=101,
                truthfulness=50,
                bias=50,
                manipulation=50,
                campaign_activity=50
            )

    def test_invalid_authenticity_low(self):
        """Test that scores < 0 are rejected."""
        with pytest.raises(ValueError):
            ComponentScores(
                authenticity=-1,
                truthfulness=50,
                bias=50,
                manipulation=50,
                campaign_activity=50
            )


class TestComponentExtraction:
    """Test component score extraction from agent results."""

    def test_extract_authenticity(self, calculator, sample_agent_results):
        """Test authenticity extraction from bot detector."""
        components = calculator._extract_component_scores(sample_agent_results)
        assert components.authenticity == 70  # 100 - (0.3 * 100)

    def test_extract_truthfulness(self, calculator, sample_agent_results):
        """Test truthfulness from fact checks."""
        components = calculator._extract_component_scores(sample_agent_results)
        # 1 false out of 3 = 33% false = ~67% truthful
        assert 66 < components.truthfulness < 68

    def test_extract_bias(self, calculator, sample_agent_results):
        """Test bias extraction."""
        components = calculator._extract_component_scores(sample_agent_results)
        assert components.bias == 0.4 or components.bias == 40

    def test_extract_manipulation(self, calculator, sample_agent_results):
        """Test manipulation extraction from emotional score."""
        components = calculator._extract_component_scores(sample_agent_results)
        assert components.manipulation == 50  # 0.5 * 100

    def test_extract_campaign(self, calculator, sample_agent_results):
        """Test campaign activity extraction."""
        components = calculator._extract_component_scores(sample_agent_results)
        assert components.campaign_activity == 30  # 0.3 * 100

    def test_missing_agents_default_to_safe_values(self, calculator):
        """Test that missing agents don't crash extraction."""
        components = calculator._extract_component_scores({})
        assert components is not None


class TestScoreCalculation:
    """Test trust score calculation."""

    def test_score_range(self, calculator, sample_agent_results):
        """Test that calculated score is 0-100."""
        result = calculator.calculate_trust_score(sample_agent_results)
        assert 0 <= result.score <= 100

    def test_moderate_content_score(self, calculator, sample_agent_results):
        """Test moderate content gets moderate score."""
        result = calculator.calculate_trust_score(sample_agent_results)
        # With 70% auth, 67% truth, high bias-inverse, etc -> moderate-to-good
        assert 40 <= result.score <= 80

    def test_high_risk_low_score(self, calculator, high_risk_results):
        """Test high-risk content gets low score."""
        result = calculator.calculate_trust_score(high_risk_results)
        assert result.score < 40

    def test_clean_content_high_score(self, calculator):
        """Test clean content gets high score."""
        clean = {
            "bot_detector": {"bot_probability": 0.05},
            "research_agent": {"fact_checks": ["TRUE", "TRUE", "TRUE"]},
            "bias_detector": {"political_bias": 0.1},
            "content_analyzer": {"emotional_score": 0.1},
            "campaign_detector": {"campaign_confidence": 0.0}
        }
        result = calculator.calculate_trust_score(clean)
        assert result.score > 70

    def test_weighting_applied(self, calculator):
        """Test that weights are applied correctly."""
        components = ComponentScores(
            authenticity=0,  # Worst
            truthfulness=100,  # Best
            bias=0,  # Best (inverse)
            manipulation=0,  # Best (inverse)
            campaign_activity=0  # Best (inverse)
        )

        score = calculator._calculate_weighted_score(components)
        # Authenticity (worst) should pull down score due to 30% weight
        assert score < 80


class TestRiskLevelAssignment:
    """Test risk level determination."""

    def test_critical_risk(self, calculator):
        """Test that low score = critical risk."""
        level = calculator._determine_risk_level(10)
        assert level == "critical"

    def test_high_risk(self, calculator):
        """Test that 21-40 = high risk."""
        level = calculator._determine_risk_level(30)
        assert level == "high"

    def test_medium_risk(self, calculator):
        """Test that 41-60 = medium risk."""
        level = calculator._determine_risk_level(50)
        assert level == "medium"

    def test_low_risk(self, calculator):
        """Test that 61+ = low risk."""
        level = calculator._determine_risk_level(75)
        assert level == "low"

    def test_boundary_critical_high(self, calculator):
        """Test boundary between critical and high (20-21)."""
        assert calculator._determine_risk_level(20) == "critical"
        assert calculator._determine_risk_level(21) == "high"

    def test_boundary_high_medium(self, calculator):
        """Test boundary between high and medium (40-41)."""
        assert calculator._determine_risk_level(40) == "high"
        assert calculator._determine_risk_level(41) == "medium"

    def test_boundary_medium_low(self, calculator):
        """Test boundary between medium and low (60-61)."""
        assert calculator._determine_risk_level(60) == "medium"
        assert calculator._determine_risk_level(61) == "low"


class TestConfidenceCalculation:
    """Test confidence score calculation."""

    def test_confidence_empty_results(self, calculator):
        """Test confidence with no agents."""
        confidence = calculator._calculate_confidence({})
        assert confidence == 0.0

    def test_confidence_single_agent(self, calculator):
        """Test confidence with single agent."""
        results = {
            "content_analyzer": {"score": 0.5},
            "bias_detector": {"bias": 0.5}
        }
        confidence = calculator._calculate_confidence(results)
        assert 0 < confidence < 1.0

    def test_confidence_all_agents(self, calculator, sample_agent_results):
        """Test confidence with all agents."""
        confidence = calculator._calculate_confidence(sample_agent_results)
        assert confidence >= 0.8  # All 6 agents present

    def test_confidence_increases_with_evidence(self, calculator):
        """Test that confidence increases with more agents."""
        two_agents = {
            "content_analyzer": {"score": 0.5},
            "bias_detector": {"bias": 0.5}
        }
        four_agents = {
            "content_analyzer": {"score": 0.5},
            "bias_detector": {"bias": 0.5},
            "bot_detector": {"prob": 0.5},
            "research_agent": {"checks": []}
        }

        conf2 = calculator._calculate_confidence(two_agents)
        conf4 = calculator._calculate_confidence(four_agents)

        assert conf4 > conf2


class TestReasoningGeneration:
    """Test reasoning text generation."""

    def test_reasoning_exists(self, calculator, sample_agent_results):
        """Test that reasoning is generated."""
        result = calculator.calculate_trust_score(sample_agent_results)
        assert result.reasoning
        assert isinstance(result.reasoning, str)
        assert len(result.reasoning) > 10

    def test_reasoning_includes_factors(self, calculator, high_risk_results):
        """Test that reasoning explains key factors."""
        result = calculator.calculate_trust_score(high_risk_results)
        reasoning_lower = result.reasoning.lower()

        # Should mention problems
        assert any(x in reasoning_lower for x in ["bot", "false", "bias", "campaign", "manipulation"])

    def test_reasoning_mentions_score(self, calculator, sample_agent_results):
        """Test that reasoning includes the score."""
        result = calculator.calculate_trust_score(sample_agent_results)
        assert str(result.score) in result.reasoning or "Score" in result.reasoning


class TestTrustScoreResult:
    """Test TrustScoreResult dataclass."""

    def test_result_structure(self, calculator, sample_agent_results):
        """Test result has all required fields."""
        result = calculator.calculate_trust_score(sample_agent_results)

        assert result.score is not None
        assert result.risk_level is not None
        assert result.component_scores is not None
        assert result.confidence is not None
        assert result.reasoning is not None

    def test_component_scores_dict(self, calculator, sample_agent_results):
        """Test component scores are in result."""
        result = calculator.calculate_trust_score(sample_agent_results)

        required_components = [
            "authenticity",
            "truthfulness",
            "bias",
            "manipulation",
            "campaign_activity"
        ]

        for comp in required_components:
            assert comp in result.component_scores

    def test_score_and_risk_alignment(self, calculator, high_risk_results):
        """Test that score and risk level are consistent."""
        result = calculator.calculate_trust_score(high_risk_results)

        if result.score < 20:
            assert result.risk_level == "critical"
        elif result.score < 40:
            assert result.risk_level == "high"
        elif result.score < 60:
            assert result.risk_level == "medium"
        else:
            assert result.risk_level == "low"
