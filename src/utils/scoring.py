"""Trust score calculation and risk assessment."""

from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class ComponentScores:
    authenticity: float
    truthfulness: float
    bias: float
    manipulation: float
    campaign_activity: float

    def __post_init__(self):
        for attr in ["authenticity", "truthfulness", "bias", "manipulation", "campaign_activity"]:
            value = getattr(self, attr)
            if not (0 <= value <= 100):
                raise ValueError(f"{attr} must be between 0-100, got {value}")


@dataclass
class TrustScoreResult:
    score: int
    risk_level: str
    component_scores: Dict[str, float]
    confidence: float
    reasoning: str


class TrustScoreCalculator:
    """Calculates evidence-based trust score (0-100)."""

    WEIGHTS = {
        "authenticity": 0.30,      # Higher = more authentic
        "truthfulness": 0.25,       # Higher = more truthful
        "bias": 0.20,               # Higher = more biased (inverse)
        "manipulation": 0.15,       # Higher = more manipulation (inverse)
        "campaign_activity": 0.10   # Higher = more campaign activity (inverse)
    }

    RISK_THRESHOLDS = {
        "critical": (0, 20),
        "high": (21, 40),
        "medium": (41, 60),
        "low": (61, 100)
    }

    def calculate_trust_score(self, agent_results: Dict[str, Any]) -> TrustScoreResult:
        """Calculate trust score from all agent findings."""
        components = self._extract_component_scores(agent_results)
        score = self._calculate_weighted_score(components)
        risk_level = self._determine_risk_level(score)
        confidence = self._calculate_confidence(agent_results)
        reasoning = self._generate_reasoning(components, score, risk_level)

        return TrustScoreResult(
            score=score,
            risk_level=risk_level,
            component_scores={
                "authenticity": components.authenticity,
                "truthfulness": components.truthfulness,
                "bias": components.bias,
                "manipulation": components.manipulation,
                "campaign_activity": components.campaign_activity
            },
            confidence=confidence,
            reasoning=reasoning
        )

    def _extract_component_scores(self, agent_results: Dict[str, Any]) -> ComponentScores:
        """Extract component scores from agent results."""
        authenticity = 100 - (agent_results.get("bot_detector", {}).get("bot_probability", 0) * 100)

        truthfulness = 100
        fact_checks = agent_results.get("research_agent", {}).get("fact_checks", [])
        if fact_checks:
            false_count = sum(1 for fc in fact_checks if "FALSE" in str(fc).upper())
            truthfulness = max(0, 100 - (false_count / len(fact_checks)) * 100)

        bias = agent_results.get("bias_detector", {}).get("political_bias", 50)

        manipulation_score = agent_results.get("content_analyzer", {}).get("emotional_score", 0.5)
        manipulation = manipulation_score * 100

        campaign = agent_results.get("campaign_detector", {}).get("campaign_confidence", 0)
        campaign_activity = campaign * 100

        return ComponentScores(
            authenticity=authenticity,
            truthfulness=truthfulness,
            bias=bias,
            manipulation=manipulation,
            campaign_activity=campaign_activity
        )

    def _calculate_weighted_score(self, components: ComponentScores) -> int:
        """Calculate weighted trust score (0-100)."""
        score = (
            (components.authenticity * self.WEIGHTS["authenticity"]) +
            (components.truthfulness * self.WEIGHTS["truthfulness"]) +
            ((100 - components.bias) * self.WEIGHTS["bias"]) +
            ((100 - components.manipulation) * self.WEIGHTS["manipulation"]) +
            ((100 - components.campaign_activity) * self.WEIGHTS["campaign_activity"])
        )
        return max(0, min(100, int(round(score))))

    def _determine_risk_level(self, score: int) -> str:
        """Map score to risk level."""
        for level, (min_val, max_val) in self.RISK_THRESHOLDS.items():
            if min_val <= score <= max_val:
                return level
        return "unknown"

    def _calculate_confidence(self, agent_results: Dict[str, Any]) -> float:
        """Calculate confidence in the score (0-1) based on evidence."""
        evidence_count = 0
        total_possible = 6

        if agent_results.get("content_analyzer"):
            evidence_count += 1
        if agent_results.get("rag_agent"):
            evidence_count += 1
        if agent_results.get("research_agent"):
            evidence_count += 1
        if agent_results.get("bias_detector"):
            evidence_count += 1
        if agent_results.get("bot_detector"):
            evidence_count += 1
        if agent_results.get("campaign_detector"):
            evidence_count += 1

        return min(1.0, evidence_count / total_possible)

    def _generate_reasoning(self, components: ComponentScores, score: int, risk_level: str) -> str:
        """Generate human-readable reasoning for the score."""
        factors = []

        if components.authenticity < 30:
            factors.append("significant bot activity detected")
        elif components.authenticity > 70:
            factors.append("authentic engagement patterns")

        if components.truthfulness < 40:
            factors.append("high rate of false claims")
        elif components.truthfulness > 70:
            factors.append("mostly truthful content")

        if components.bias > 70:
            factors.append("strong political/ideological bias")

        if components.manipulation > 70:
            factors.append("heavy emotional manipulation detected")

        if components.campaign_activity > 60:
            factors.append("part of coordinated campaign")

        factors_str = "; ".join(factors) if factors else "mixed evidence"

        return f"Score {score} ({risk_level}): {factors_str}."
