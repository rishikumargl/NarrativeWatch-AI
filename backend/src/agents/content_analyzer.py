from src.llm.groq_client import groq_client
from src.ml_models_local import local_models
from src.utils.entity_extractor import EntityExtractor
import json
import logging
import re

logger = logging.getLogger(__name__)

class ContentAnalyzerAgent:
    """Extract features, claims, and narrative themes with real ML analysis"""

    def __init__(self, llm, ml):
        self.llm = llm
        self.ml = ml

    async def analyze(self, article_text: str, title: str) -> dict:
        """Analyze article using real ML models"""
        logger.info("Content analyzer starting...")

        findings = {
            "title": title,
            "analysis": {}
        }

        # 1. REAL SENTIMENT ANALYSIS
        logger.info("Running sentiment analysis...")
        sentiment = await self.ml.analyze_sentiment(article_text)
        findings["analysis"]["sentiment"] = sentiment

        # 2. TOXICITY DETECTION
        logger.info("Detecting toxicity...")
        toxicity = await self.ml.detect_toxicity(article_text)
        findings["analysis"]["toxicity"] = toxicity

        # 3. PROPAGANDA DETECTION
        logger.info("Detecting propaganda...")
        propaganda = await self.ml.detect_propaganda(article_text)
        findings["analysis"]["propaganda"] = propaganda

        # 4. ENHANCED ENTITY EXTRACTION WITH SCORING
        logger.info("Extracting and scoring entities...")
        entities = await EntityExtractor.extract_and_score_entities(article_text)
        findings["analysis"]["entities"] = entities

        # 5. MISINFORMATION CLASSIFICATION
        logger.info("Classifying misinformation likelihood...")
        misinfo = await self.ml.classify_misinformation(article_text)
        findings["analysis"]["misinformation"] = misinfo

        # 6. EXTRACT CLAIMS AND THEMES
        claims = self._extract_claims(article_text)
        findings["analysis"]["claims"] = claims

        # Entity count from enhanced extraction
        entity_count = entities.get("total_count", 0) if isinstance(entities, dict) else 0
        findings["analysis"]["entity_count"] = entity_count

        findings["analysis"]["sensationalism_score"] = self._calculate_sensationalism(article_text)
        findings["analysis"]["emotional_language_detected"] = sentiment.get("label") != "NEUTRAL"

        logger.info(f"Content analysis complete - Found {entity_count} key entities")

        return {
            "agent": "content_analyzer",
            "status": "completed",
            "findings": findings,
            "confidence": 0.90
        }

    def _extract_claims(self, text: str) -> list:
        """Extract main claims from text"""
        sentences = text.split(".")[:5]  # First 5 sentences
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    def _extract_key_entities(self, text: str) -> list:
        """Extract key entities using regex and keyword matching"""
        entities = []

        # Find capitalized phrases (proper nouns)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend(proper_nouns)

        # Extract common named entities by pattern
        # Countries, organizations, people names
        keywords = {
            'countries': r'\b(United States|Russia|China|India|Germany|France|UK|USA|UN|NATO)\b',
            'orgs': r'\b(Government|Military|Army|Congress|Parliament|Company|Corp|Inc)\b',
            'people': r'\b(President|Minister|King|Queen|General|Colonel|Leader)\b'
        }

        for key, pattern in keywords.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)

        # Return unique entities, up to 15
        return list(set(entities))[:15] if entities else ["General Topic"]

    def _calculate_sensationalism(self, text: str) -> float:
        """Calculate sensationalism score"""
        sensational_words = ["shocking", "devastating", "outrageous", "unbelievable", "horror", "crisis", "catastrophe"]
        count = sum(1 for word in sensational_words if word in text.lower())
        score = min(10, (count / max(1, len(text.split()))) * 1000)
        return round(score, 1)

content_analyzer = ContentAnalyzerAgent(groq_client.get_llm(), local_models)
