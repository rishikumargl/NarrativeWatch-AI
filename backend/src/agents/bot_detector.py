from src.llm.groq_client import groq_client
from src.ml_models_local import local_models
import json
import logging
import re

logger = logging.getLogger(__name__)

class BotDetectorAgent:
    """Detect inauthentic engagement and bot activity"""

    def __init__(self, llm, ml):
        self.llm = llm
        self.ml = ml

    def calculate_bot_probability(self, text: str) -> int:
        """Calculate bot probability from text analysis"""
        bot_score = 5  # Base score
        words = text.lower().split()

        # Check for repetitive patterns (high uniqueness = less repetitive = less bot-like)
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            # If low uniqueness, increase bot score
            bot_score += (1 - unique_ratio) * 40  # 0-40 points

        # Check for automated/spam patterns
        automated_patterns = [
            (r'(?:follow|subscribe|click|like|visit|buy|follow us|visit us)\s+(?:now|here|this|link|today)', 15),
            (r'(?:rt|retweet|share|tag|dm|inbox)', 10),
            (r'(?:bot|automated|script|macro|auto)', 20),
            (r'(?:http|www|\.com|click here)', 5),  # URLs increase bot likelihood
        ]

        for pattern, points in automated_patterns:
            if re.search(pattern, text):
                bot_score += points

        # Check for excessive punctuation (common in spam)
        exclamation_count = text.count('!')
        question_count = text.count('?')
        if exclamation_count >= 2 or question_count >= 2:
            bot_score += 10

        return min(100, max(0, int(bot_score)))

    async def analyze_engagement(self, article_url: str, article_text: str = "", context: dict = None) -> dict:
        """Analyze text for bot patterns and inauthentic markers with optional enriched context"""
        logger.info("Bot detection analyzing article text...")

        if context:
            logger.info(f"🔍 Using enriched context: {context.get('news_coverage', {}).get('similar_articles_found', 0)} corroborating sources for pattern analysis")
        findings = {"url": article_url}

        if article_text:
            # Calculate bot probability from text
            bot_prob = self.calculate_bot_probability(article_text)
            findings["bot_probability"] = bot_prob

            # Detect toxicity
            toxicity = await self.ml.detect_toxicity(article_text)
            findings["toxicity"] = toxicity

            # Detect offensive language
            offensive = await self.ml.detect_offensive_language(article_text)
            findings["offensive_language"] = offensive

            # Determine authenticity score
            authenticity = max(0, 100 - bot_prob - (toxicity.get("toxicity_score", 0) / 2))
            findings["authenticity_score"] = int(authenticity)
        else:
            findings["bot_probability"] = 0
            findings["authenticity_score"] = 100

        findings["bot_analysis"] = {
            "bot_probability": findings.get("bot_probability", 0),
            "authenticity_score": findings.get("authenticity_score", 100),
            "offensive_language": findings.get("offensive_language", {}),
            "toxicity": findings.get("toxicity", {})
        }

        return {
            "agent": "bot_detector",
            "status": "completed",
            "findings": findings,
            "confidence": 0.85
        }

bot_detector = BotDetectorAgent(groq_client.get_llm(), local_models)
