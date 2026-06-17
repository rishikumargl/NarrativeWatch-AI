from src.llm.groq_client import groq_client
from src.ml_models_local import local_models
import json
import logging
import re

logger = logging.getLogger(__name__)

class MisinformationDetector:
    """Specialized misinformation and propaganda detection"""
    
    def __init__(self, llm, ml):
        self.llm = llm
        self.ml = ml
    
    async def detect_misinformation(self, article_text: str, title: str = "", context: dict = None) -> dict:
        """Detect misinformation with multiple techniques and optional enriched context"""

        logger.info("Starting misinformation detection...")

        if context:
            logger.info(f"🔍 Using enriched context: {context.get('news_coverage', {}).get('similar_articles_found', 0)} corroborating sources for fact-checking context")

        findings = {
            "title": title,
            "misinformation_analysis": {}
        }

        # 1. ML MISINFORMATION CLASSIFICATION
        logger.info("Running ML misinformation classifier...")
        misinfo_ml = await self.ml.classify_misinformation(article_text)
        findings["misinformation_analysis"]["ml_classification"] = misinfo_ml

        # 2. PROPAGANDA TECHNIQUES DETECTION
        logger.info("Detecting propaganda techniques...")
        propaganda_techniques = self._detect_propaganda_techniques(article_text)
        findings["misinformation_analysis"]["propaganda_techniques"] = propaganda_techniques

        # 3. UNVERIFIED CLAIMS DETECTION (NEW)
        logger.info("Detecting unverified claims...")
        unverified_claims = self._detect_unverified_claims(article_text)
        findings["misinformation_analysis"]["unverified_claims"] = unverified_claims

        # 4. CLAIM VERIFICATION READINESS
        logger.info("Assessing claim verifiability...")
        verifiability = self._assess_verifiability(article_text)
        findings["misinformation_analysis"]["verifiability_score"] = verifiability

        # 5. SOURCE CREDIBILITY MARKERS
        logger.info("Analyzing source credibility markers...")
        credibility_markers = self._analyze_credibility_markers(article_text)
        findings["misinformation_analysis"]["credibility_indicators"] = credibility_markers

        # 6. EMOTIONAL MANIPULATION DETECTION
        logger.info("Detecting emotional manipulation...")
        emotional_manipulation = self._detect_emotional_manipulation(article_text)
        findings["misinformation_analysis"]["emotional_manipulation"] = emotional_manipulation

        # 7. FINAL MISINFORMATION SCORE (Weighted with unverified claims)
        ml_score = misinfo_ml.get("misinformation_likelihood", 0)
        propaganda_score = sum(propaganda_techniques.values()) / len(propaganda_techniques) if propaganda_techniques else 0
        unverified_score = unverified_claims.get("unverified_risk", 0)
        emotional_score = emotional_manipulation.get("manipulation_score", 0)

        final_score = (ml_score * 0.30 + propaganda_score * 0.25 + unverified_score * 0.25 + emotional_score * 0.20)
        findings["misinformation_analysis"]["final_misinformation_score"] = round(min(100, max(0, final_score)), 1)
        
        # Risk level
        if final_score > 75:
            risk_level = "CRITICAL"
        elif final_score > 55:
            risk_level = "HIGH"
        elif final_score > 35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        findings["misinformation_analysis"]["risk_level"] = risk_level
        
        return {
            "agent": "misinformation_detector",
            "status": "completed",
            "findings": findings,
            "confidence": 0.91,
            "accuracy_source": "ML + Propaganda detection + Emotional analysis + Credibility assessment"
        }
    
    def _detect_unverified_claims(self, text: str) -> dict:
        """Detect unverified and potentially false claims"""
        unverified_keywords = [
            r'allegedly', r'reportedly', r'claims', r'sources say',
            r'it is believed', r'some say', r'unconfirmed', r'rumor',
            r'leaked', r'insider sources', r'whistleblower', r'anonymous'
        ]

        claim_markers = [
            'nuclear', 'weapons', 'ceasefire', 'peace deal', 'treaty',
            'breakthrough', 'agreement', 'surrender', 'victory', 'defeat'
        ]

        # Count unverified language
        unverified_count = sum(1 for kw in unverified_keywords if re.search(kw, text.lower()))

        # Count significant claims
        claim_count = sum(1 for cm in claim_markers if cm in text.lower())

        # Calculate risk: high claim count with unverified language = high risk
        unverified_risk = 0
        if claim_count > 0:
            unverified_ratio = unverified_count / max(1, claim_count)
            unverified_risk = min(100, unverified_ratio * 50 + claim_count * 5)

        # If significant claims present but no sources, higher risk
        if claim_count > 2 and "source" not in text.lower() and "according" not in text.lower():
            unverified_risk = min(100, unverified_risk + 20)

        return {
            "unverified_claims_count": unverified_count,
            "significant_claims_count": claim_count,
            "unverified_risk": round(max(10, unverified_risk), 1)
        }

    def _detect_propaganda_techniques(self, text: str) -> dict:
        """Detect common propaganda techniques"""
        techniques = {
            "loaded_language": 0,
            "bandwagon": 0,
            "false_dilemma": 0,
            "appeal_to_emotion": 0,
            "ad_hominem": 0,
            "red_herring": 0,
            "glittering_generalities": 0
        }
        
        patterns = {
            "loaded_language": r"(evil|corrupt|criminals|monsters|patriots|heroes)",
            "bandwagon": r"(everyone|all people|most experts|everyone knows|widely accepted)",
            "false_dilemma": r"(either|or|only option|must choose)",
            "appeal_to_emotion": r"(horrifying|devastating|unbelievable|shocking|outrageous)",
            "ad_hominem": r"(fool|idiot|stupid|unintelligent)",
            "red_herring": r"(btw|anyway|aside from|by the way)",
            "glittering_generalities": r"(freedom|justice|truth|equality|democracy)"
        }
        
        for technique, pattern in patterns.items():
            matches = len(re.findall(pattern, text.lower()))
            techniques[technique] = min(100, (matches / len(text.split())) * 1000)
        
        return {k: round(v, 1) for k, v in techniques.items()}
    
    def _assess_verifiability(self, text: str) -> float:
        """Assess how verifiable the claims are"""
        specific_claims = len(re.findall(r"\d+%|\d+ million|\d+ billion|[A-Z][a-z]+ said", text))
        vague_claims = len(re.findall(r"some|many|most|allegedly|reportedly", text))
        
        verifiability = (specific_claims - vague_claims) / max(1, specific_claims + vague_claims) * 100
        return round(max(0, min(100, verifiability + 50)), 1)
    
    def _analyze_credibility_markers(self, text: str) -> dict:
        """Analyze markers of credibility"""
        return {
            "has_sources": 50 if "source" in text.lower() or "according" in text.lower() else 0,
            "has_citations": 30 if "[" in text or "(" in text else 0,
            "professional_tone": 40 if not re.search(r"!!!|\?\?\?|lol|haha", text) else 0,
            "transparency": 25 if "I believe" not in text.lower() else 40
        }
    
    def _detect_emotional_manipulation(self, text: str) -> dict:
        """Detect emotional manipulation techniques with enhanced scoring"""
        # Expanded emotional/manipulative keywords
        negative_emotional = [
            "shocking", "devastating", "unbelievable", "outrageous",
            "horrible", "terrifying", "disgusting", "pathetic", "tragic",
            "dramatic", "crisis", "catastrophe", "disaster", "emergency",
            "nightmare", "hell", "war", "attack", "bomb", "kill", "death",
            "bloodshed", "massacre", "genocide", "terror", "horror"
        ]

        positive_emotional = [
            "amazing", "wonderful", "beautiful", "incredible", "fantastic",
            "stunning", "perfect", "ideal", "best", "greatest",
            "victory", "triumph", "peace", "hope", "salvation"
        ]

        extremist_words = [
            "always", "never", "everyone", "nobody", "must",
            "absolutely", "definitely", "certainly", "obviously",
            "clearly", "undeniably", "without question"
        ]

        # Count occurrences with word boundaries
        negative_count = sum(1 for word in negative_emotional if word in text.lower())
        positive_count = sum(1 for word in positive_emotional if word in text.lower())
        extremist_count = len(re.findall(r'\b(' + '|'.join(extremist_words) + r')\b', text.lower()))

        total_words = len(text.split())
        # Reduce multipliers - news articles naturally have emotional language
        manipulation_count = (negative_count * 1.0) + (positive_count * 0.8) + (extremist_count * 0.7)

        # Calculate score (0-100) - much more conservative for news content
        base_score = (manipulation_count / max(1, total_words)) * 40
        manipulation_score = min(75, max(5, base_score))

        return {
            "manipulation_score": round(manipulation_score, 1),
            "emotional_intensity": "CRITICAL" if manipulation_score > 70 else "HIGH" if manipulation_score > 50 else "MEDIUM" if manipulation_score > 30 else "LOW",
            "negative_emotional_words": negative_count,
            "positive_emotional_words": positive_count,
            "extremist_language_count": extremist_count
        }

misinformation_detector = MisinformationDetector(groq_client.get_llm(), local_models)
