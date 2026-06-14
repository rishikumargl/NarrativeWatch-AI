from src.llm.groq_client import groq_client
from src.ml_models_local import local_models
import json
import logging
import re

logger = logging.getLogger(__name__)

class BiasDetectorAgent:
    """Detect political, gender, religious, and ideological bias using ML"""

    def __init__(self, llm, ml):
        self.llm = llm
        self.ml = ml

    async def detect_bias(self, article_text: str, title: str) -> dict:
        """Detect bias using real ML models"""
        logger.info("Bias detector starting...")

        findings = {
            "title": title,
            "bias_analysis": {}
        }

        # 1. USE ML MODEL FOR BIAS DETECTION
        logger.info("Running ML bias detection...")
        bias_result = await self.ml.detect_bias(article_text)
        findings["bias_analysis"]["ml_detected_biases"] = bias_result

        # 2. PATTERN-BASED BIAS DETECTION (0-100 scale)
        bias_scores = {
            "political_bias": self._detect_political_bias(article_text),
            "gender_bias": self._detect_gender_bias(article_text),
            "religious_bias": self._detect_religious_bias(article_text),
            "ideological_bias": self._detect_ideological_bias(article_text),
            "socioeconomic_bias": self._detect_socioeconomic_bias(article_text)
        }

        findings["bias_analysis"]["pattern_based_biases"] = bias_scores

        # 3. CALCULATE OVERALL BIAS SCORE (0-100)
        scores = [score for score in bias_scores.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        findings["bias_analysis"]["overall_bias_score"] = round(overall_score, 1)

        # Determine bias level based on 0-100 scale
        if overall_score > 70:
            bias_level = "CRITICAL"
        elif overall_score > 50:
            bias_level = "HIGH"
        elif overall_score > 30:
            bias_level = "MEDIUM"
        else:
            bias_level = "LOW"

        findings["bias_analysis"]["overall_bias_level"] = bias_level

        logger.info("Bias detection complete")

        return {
            "agent": "bias_detector",
            "status": "completed",
            "findings": findings,
            "confidence": 0.88
        }

    def _detect_political_bias(self, text: str) -> float:
        """Detect political bias using keyword patterns (0-100 scale)"""
        left_wing = len(re.findall(r'\b(socialist|progressive|liberal|democrat|left|equality|social justice|justice|rights)\b', text.lower()))
        right_wing = len(re.findall(r'\b(conservative|capitalist|republican|right|freedom|traditional|order|security)\b', text.lower()))

        if left_wing == 0 and right_wing == 0:
            return 5.0  # Base bias score for neutral text
        score = abs(left_wing - right_wing) / max(1, (left_wing + right_wing)) * 100
        return min(100, max(5, score))

    def _detect_gender_bias(self, text: str) -> float:
        """Detect gender bias (0-100 scale)"""
        male_refs = len(re.findall(r'\bhe\b|\bhis\b|\bhim\b|\bman\b|\bmen\b|\bking\b|\bboy\b', text.lower()))
        female_refs = len(re.findall(r'\bshe\b|\bher\b|\bwoman\b|\bwomen\b|\bqueen\b|\bgirl\b', text.lower()))

        if male_refs == 0 and female_refs == 0:
            return 5.0  # Base gender bias for neutral text
        total = male_refs + female_refs
        score = abs(male_refs - female_refs) / total * 100
        return min(100, max(5, score))

    def _detect_religious_bias(self, text: str) -> float:
        """Detect religious bias (0-100 scale)"""
        positive_religious = len(re.findall(r'\b(christian|muslim|jewish|hindu|buddhist|faith|moral|spiritual|holy|sacred)\b', text.lower(), re.IGNORECASE))
        negative_religious = len(re.findall(r'\b(atheist|godless|immoral|heretic|infidel|pagan)\b', text.lower(), re.IGNORECASE))

        score = abs(positive_religious - negative_religious) / max(1, positive_religious + negative_religious + 1) * 100
        return min(100, max(5, score))

    def _detect_ideological_bias(self, text: str) -> float:
        """Detect ideological bias (0-100 scale)"""
        dogmatic_language = len(re.findall(r'\b(must|clearly|obviously|everyone knows|undeniable|always|never|definitely)\b', text.lower()))
        words = len(text.split())
        score = (dogmatic_language / max(1, words)) * 10000
        return min(100, max(5, score))

    def _detect_socioeconomic_bias(self, text: str) -> float:
        """Detect socioeconomic bias (0-100 scale)"""
        elitist = len(re.findall(r'\b(elite|inferior|superior|primitive|civilized|uneducated|intelligent|educated)\b', text.lower()))
        classist = len(re.findall(r'\b(poor|rich|wealthy|lower|upper|class|worker|wealthy)\b', text.lower()))

        words = len(text.split())
        score = ((elitist + classist) / max(1, words)) * 10000
        return min(100, max(5, score))

bias_detector = BiasDetectorAgent(groq_client.get_llm(), local_models)
