"""Bias Detector Agent for NarrativeWatch AI."""

from typing import Dict, Any, List
from datetime import datetime
import logging
import re

try:
    from src.agents.base_agent import BaseAgent
    from src.utils.text_processor import TextProcessor
except ImportError:
    from base_agent import BaseAgent
    from sys import path
    from os import dirname
    path.insert(0, dirname(dirname(__file__)))
    from utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class BiasDetectorAgent(BaseAgent):
    """Detect political, gender, and ideological bias in content."""

    def __init__(self):
        """Initialize Bias Detector Agent."""
        super().__init__(
            name="Bias Detector",
            description="Identify political, gender, and ideological bias in content "
                       "with confidence scores"
        )
        self.text_processor = TextProcessor()
        self.political_keywords = self._init_political_keywords()
        self.gender_keywords = self._init_gender_keywords()
        self.ideology_keywords = self._init_ideology_keywords()

    def run(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content for various types of bias.

        Args:
            content: Dict with text, caption, comments, etc.

        Returns:
            Dict with bias analysis results
        """
        try:
            if not self.validate_input(content):
                return {"status": "error", "message": "Invalid input data"}

            text = content.get("text", "")
            additional_text = content.get("comments", [])
            all_text = text + " " + " ".join(additional_text)

            analysis = {
                "political_bias": self._detect_political_bias(all_text),
                "gender_bias": self._detect_gender_bias(all_text),
                "ideological_bias": self._detect_ideological_bias(all_text),
                "toxicity_score": self._calculate_toxicity(all_text),
                "overall_bias_score": 0.0,  # Calculated below
                "bias_indicators": self._extract_bias_indicators(all_text),
            }

            # Calculate overall bias score
            political_intensity = max(
                analysis["political_bias"]["left_score"],
                analysis["political_bias"]["right_score"]
            )
            gender_intensity = max(
                analysis["gender_bias"]["male_bias"],
                analysis["gender_bias"]["female_bias"]
            )
            ideology_intensity = max(
                analysis["ideological_bias"]["progressive_score"],
                analysis["ideological_bias"]["conservative_score"]
            )

            analysis["overall_bias_score"] = (
                political_intensity * 0.4 +
                gender_intensity * 0.3 +
                ideology_intensity * 0.2 +
                analysis["toxicity_score"] * 0.1
            )

            return {
                "status": "success",
                "agent": "Bias Detector",
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Bias Detector error: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def validate_input(self, input_data: Any) -> bool:
        """Validate input data."""
        if not isinstance(input_data, dict):
            return False
        if "text" not in input_data:
            return False
        return True

    def _detect_political_bias(self, text: str) -> Dict[str, Any]:
        """Detect political bias in text."""
        text_lower = text.lower()

        left_score = self._calculate_keyword_score(text_lower, self.political_keywords["left"])
        right_score = self._calculate_keyword_score(text_lower, self.political_keywords["right"])
        center_score = self._calculate_keyword_score(text_lower, self.political_keywords["center"])

        # Normalize scores
        total = left_score + right_score + center_score
        if total > 0:
            left_score = left_score / total
            right_score = right_score / total
            center_score = center_score / total
        else:
            left_score = center_score = right_score = 1/3

        # Determine bias direction
        if left_score > right_score and left_score > center_score:
            bias_direction = "left"
        elif right_score > left_score and right_score > center_score:
            bias_direction = "right"
        else:
            bias_direction = "center"

        return {
            "left_score": float(left_score),
            "center_score": float(center_score),
            "right_score": float(right_score),
            "bias_direction": bias_direction,
            "confidence": float(max(left_score, right_score, center_score)),
        }

    def _detect_gender_bias(self, text: str) -> Dict[str, Any]:
        """Detect gender bias in text."""
        text_lower = text.lower()

        male_bias = self._calculate_keyword_score(text_lower, self.gender_keywords["male"])
        female_bias = self._calculate_keyword_score(text_lower, self.gender_keywords["female"])
        neutral_bias = self._calculate_keyword_score(text_lower, self.gender_keywords["neutral"])

        # Normalize
        total = male_bias + female_bias + neutral_bias
        if total > 0:
            male_bias = male_bias / total
            female_bias = female_bias / total
            neutral_bias = neutral_bias / total
        else:
            male_bias = female_bias = neutral_bias = 1/3

        # Determine gender bias direction
        if male_bias > female_bias and male_bias > neutral_bias:
            bias_direction = "male_bias"
        elif female_bias > male_bias and female_bias > neutral_bias:
            bias_direction = "female_bias"
        else:
            bias_direction = "neutral"

        return {
            "male_bias": float(male_bias),
            "female_bias": float(female_bias),
            "neutral": float(neutral_bias),
            "bias_direction": bias_direction,
            "confidence": float(max(male_bias, female_bias, neutral_bias)),
        }

    def _detect_ideological_bias(self, text: str) -> Dict[str, Any]:
        """Detect ideological bias in text."""
        text_lower = text.lower()

        progressive = self._calculate_keyword_score(text_lower, self.ideology_keywords["progressive"])
        conservative = self._calculate_keyword_score(text_lower, self.ideology_keywords["conservative"])
        moderate = self._calculate_keyword_score(text_lower, self.ideology_keywords["moderate"])

        # Normalize
        total = progressive + conservative + moderate
        if total > 0:
            progressive = progressive / total
            conservative = conservative / total
            moderate = moderate / total
        else:
            progressive = conservative = moderate = 1/3

        # Determine ideological direction
        if progressive > conservative and progressive > moderate:
            ideology_direction = "progressive"
        elif conservative > progressive and conservative > moderate:
            ideology_direction = "conservative"
        else:
            ideology_direction = "moderate"

        return {
            "progressive_score": float(progressive),
            "conservative_score": float(conservative),
            "moderate_score": float(moderate),
            "ideology_direction": ideology_direction,
            "confidence": float(max(progressive, conservative, moderate)),
        }

    def _calculate_toxicity(self, text: str) -> float:
        """Calculate toxicity score (0-1)."""
        toxic_keywords = [
            "hate", "kill", "die", "stupid", "idiot", "moron",
            "offensive", "disgusting", "vile", "despicable"
        ]

        text_lower = text.lower()
        toxic_count = sum(1 for keyword in toxic_keywords if keyword in text_lower)

        # Normalize by text length
        words = len(text.split())
        if words == 0:
            return 0.0

        toxicity = min(toxic_count / (words / 10), 1.0)
        return float(toxicity)

    def _extract_bias_indicators(self, text: str) -> List[Dict[str, str]]:
        """Extract specific phrases indicating bias."""
        indicators = []
        text_lower = text.lower()

        # Define bias phrases
        bias_phrases = {
            "political": [
                "liberals are", "conservatives are", "democrats are", "republicans are",
                "the left", "the right", "leftists", "rightists"
            ],
            "gender": [
                "all women", "all men", "women should", "men should",
                "female privilege", "male privilege"
            ],
            "ideological": [
                "true patriot", "woke culture", "social justice warrior",
                "safe space", "cancel culture"
            ]
        }

        for bias_type, phrases in bias_phrases.items():
            for phrase in phrases:
                if phrase in text_lower:
                    indicators.append({
                        "phrase": phrase,
                        "type": bias_type,
                        "severity": "high" if len(phrase.split()) > 2 else "medium",
                    })

        return indicators

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate score based on keyword presence."""
        score = 0.0
        for keyword in keywords:
            count = text.count(keyword)
            score += count

        return min(score / 10, 1.0)  # Normalize

    def _init_political_keywords(self) -> Dict[str, List[str]]:
        """Initialize political keywords."""
        return {
            "left": [
                "liberal", "progressive", "democrat", "left-wing", "socialism",
                "social justice", "climate change", "healthcare", "worker",
                "inequality", "marginalized", "systemic racism"
            ],
            "right": [
                "conservative", "republican", "right-wing", "capitalism",
                "freedom", "liberty", "border", "immigration restriction",
                "traditional values", "national security", "law and order"
            ],
            "center": [
                "bipartisan", "moderate", "independent", "centrist",
                "balanced", "compromise", "both sides"
            ]
        }

    def _init_gender_keywords(self) -> Dict[str, List[str]]:
        """Initialize gender keywords."""
        return {
            "male": [
                "man", "men", "male", "masculine", "boys", "he", "him",
                "father", "husband", "brother", "son"
            ],
            "female": [
                "woman", "women", "female", "feminine", "girls", "she", "her",
                "mother", "wife", "sister", "daughter"
            ],
            "neutral": [
                "person", "people", "they", "them", "human", "individual",
                "someone", "everyone", "anyone"
            ]
        }

    def _init_ideology_keywords(self) -> Dict[str, List[str]]:
        """Initialize ideological keywords."""
        return {
            "progressive": [
                "equality", "justice", "diversity", "inclusion", "change",
                "reform", "progress", "future", "innovation", "evolution"
            ],
            "conservative": [
                "tradition", "stability", "heritage", "proven", "established",
                "classical", "time-tested", "values", "order", "preservation"
            ],
            "moderate": [
                "balance", "pragmatic", "reasonable", "practical", "realistic",
                "nuanced", "flexible", "adaptive"
            ]
        }
