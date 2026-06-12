"""Example implementations of missing agents for integration testing.

These are placeholder/example agents that show the interface other teams should implement.
Teams can replace these with their actual implementations.
"""

import logging
from typing import List, Optional
from src.agents.orchestrator import BiasAnalysisResult, BotAnalysisResult, MisinformationResult

logger = logging.getLogger(__name__)


class ExampleBiasAgent:
    """Example bias detection agent implementation.

    Replace with actual ML/NLP implementation by bias detection team.
    """

    def detect_bias(
        self,
        caption: str,
        hashtags: Optional[List[str]] = None,
    ) -> BiasAnalysisResult:
        """Detect bias in content.

        Args:
            caption: Content text
            hashtags: Associated hashtags

        Returns:
            BiasAnalysisResult with findings
        """
        # Placeholder: Real implementation would use ML models
        # Example: gender bias detection

        bias_indicators = {
            "she": ["pronoun", "female"],
            "he": ["pronoun", "male"],
            "woman": ["gender", "female"],
            "man": ["gender", "male"],
        }

        detected_indicators = []
        bias_score = 0.0
        bias_categories = []

        # Simple keyword matching (real: use ML models)
        text = (caption + " " + " ".join(hashtags or [])).lower()

        for word, indicators in bias_indicators.items():
            if word in text:
                detected_indicators.extend(indicators)
                bias_score += 0.15
                if "female" in indicators or "male" in indicators:
                    if "gender" not in bias_categories:
                        bias_categories.append("gender")

        bias_score = min(1.0, bias_score)
        bias_detected = bias_score > 0.3

        return BiasAnalysisResult(
            bias_detected=bias_detected,
            bias_categories=bias_categories or ["none"],
            bias_score=bias_score,
            indicators=list(set(detected_indicators)),
            description=f"Detected {len(detected_indicators)} bias indicators"
            if bias_detected
            else "No significant bias detected",
        )


class ExampleBotAgent:
    """Example bot detection agent implementation.

    Replace with actual implementation by data engineering team.
    """

    def detect_bot(
        self,
        page: str,
        engagement: tuple = (0, 0),
    ) -> BotAnalysisResult:
        """Detect bot-like behavior.

        Args:
            page: Page username
            engagement: Tuple of (likes, comments)

        Returns:
            BotAnalysisResult with findings
        """
        # Placeholder: Real implementation would use engagement patterns
        # Example: suspicious engagement ratios

        likes, comments = engagement
        total_engagement = likes + comments

        # Simple heuristics (real: use ML models + pattern analysis)
        engagement_ratio = comments / max(1, likes)  # Expect 5-10% comment rate
        automation_likelihood = 0.0
        indicators = []

        # Suspicious if too few comments relative to likes
        if engagement_ratio < 0.01 and total_engagement > 100:
            automation_likelihood += 0.3
            indicators.append("low_comment_ratio")

        # Suspicious if engagement is suspiciously round
        if likes > 0 and likes % 100 == 0:
            automation_likelihood += 0.2
            indicators.append("round_engagement_numbers")

        # Username patterns (real: use NLP)
        if any(
            c.isdigit()
            for c in page
            if page.count(c) > 3
        ):  # Many repeated digits
            automation_likelihood += 0.15
            indicators.append("numeric_username")

        automation_likelihood = min(1.0, automation_likelihood)
        bot_score = automation_likelihood
        bot_detected = bot_score > 0.4

        engagement_pattern = (
            "suspicious"
            if bot_detected
            else ("normal" if total_engagement > 50 else "low_engagement")
        )

        return BotAnalysisResult(
            bot_detected=bot_detected,
            bot_score=bot_score,
            indicators=indicators or ["none"],
            engagement_pattern=engagement_pattern,
            automation_likelihood=automation_likelihood,
        )


class ExampleMisinformationAgent:
    """Example misinformation detection agent implementation.

    Replace with actual implementation by data engineering team.
    """

    def detect_misinformation(
        self,
        caption: str,
        hashtags: Optional[List[str]] = None,
    ) -> MisinformationResult:
        """Detect misleading or false claims.

        Args:
            caption: Content text
            hashtags: Associated hashtags

        Returns:
            MisinformationResult with findings
        """
        # Placeholder: Real implementation would use fact-checking databases
        # Example: claim detection

        suspicious_patterns = {
            "fact: ": "claim",
            "scientists say": "unverified",
            "doctors recommend": "unverified",
            "studies show": "unverified",
            "proven": "strong_claim",
            "100% effective": "exaggeration",
            "miracle": "exaggeration",
        }

        text = (caption + " " + " ".join(hashtags or [])).lower()
        contradictions = []
        verified_claims = []
        claim_accuracy = 1.0

        # Detect suspicious claims (real: use fact-checking API)
        for pattern, claim_type in suspicious_patterns.items():
            if pattern in text:
                if claim_type in ["unverified", "exaggeration"]:
                    contradictions.append(f"Detected {claim_type}: {pattern}")
                    claim_accuracy -= 0.15
                elif claim_type == "claim":
                    verified_claims.append(pattern)

        claim_accuracy = max(0.0, min(1.0, claim_accuracy))
        misleading = claim_accuracy < 0.7
        research_credibility = (
            "LOW"
            if claim_accuracy < 0.5
            else ("MEDIUM" if claim_accuracy < 0.8 else "HIGH")
        )

        return MisinformationResult(
            misleading_content=misleading,
            claim_accuracy=claim_accuracy,
            contradictions=contradictions or ["none"],
            verified_claims=verified_claims or ["none"],
            research_credibility=research_credibility,
        )


def get_example_agents() -> tuple:
    """Get example agent instances.

    Returns:
        Tuple of (bias_agent, bot_agent, misinformation_agent)
    """
    return (
        ExampleBiasAgent(),
        ExampleBotAgent(),
        ExampleMisinformationAgent(),
    )
