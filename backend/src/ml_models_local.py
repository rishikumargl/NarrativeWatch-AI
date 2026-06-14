"""Local ML Models - Download once, run offline"""
import logging
from transformers import pipeline
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=2)

class LocalMLModels:
    """Run ML models locally without API calls"""

    def __init__(self):
        logger.info("Initializing local ML models...")

        try:
            # Sentiment analysis - fast and accurate
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1  # CPU
            )
            logger.info("Sentiment model loaded")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            self.sentiment_pipeline = None

        try:
            # Zero-shot classification for bias detection
            self.zero_shot = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1
            )
            logger.info("Bias detection model loaded")
        except Exception as e:
            logger.error(f"Failed to load bias model: {e}")
            self.zero_shot = None

        try:
            # NER for entity extraction - use smaller, more reliable model
            self.ner_pipeline = pipeline(
                "ner",
                model="bert-base-cased",
                aggregation_strategy="simple",
                device=-1
            )
            logger.info("NER model loaded")
        except Exception as e:
            logger.warning(f"Trying alternative NER model: {e}")
            try:
                # Fallback to simpler model
                self.ner_pipeline = pipeline(
                    "ner",
                    model="Jean-Baptiste/camembert-ner",
                    device=-1
                )
                logger.info("Alternative NER model loaded")
            except Exception as e2:
                logger.warning(f"NER model unavailable, will extract keywords instead: {e2}")
                self.ner_pipeline = None

        logger.info("Local ML models initialized")

    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using local model"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: self.sentiment_pipeline(text[:512])
            )

            label = result[0]['label'].lower()
            score = result[0]['score']

            return {
                "label": label,
                "score": round(score, 3),
                "confidence": round(score * 100, 1)
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"label": "neutral", "score": 0.5, "confidence": 50.0}

    async def detect_bias(self, text: str) -> dict:
        """Detect bias using zero-shot classification"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: self.zero_shot(
                    text[:512],
                    ["biased", "neutral"],
                    multi_class=False
                )
            )

            # Get the bias score
            bias_score = 0
            for label, score in zip(result['labels'], result['scores']):
                if label == 'biased':
                    bias_score = score
                    break

            return {
                "detected_biases": {},
                "max_bias": round(bias_score, 2),
                "overall_bias_level": "high" if bias_score > 0.6 else "low"
            }
        except Exception as e:
            logger.error(f"Bias detection error: {e}")
            return {"detected_biases": {}, "max_bias": 0, "overall_bias_level": "low"}

    async def extract_entities(self, text: str) -> dict:
        """Extract named entities using simple keyword matching"""
        try:
            # Simple keyword-based entity extraction (more reliable than NER)
            import re

            parsed = {"PERSON": [], "ORG": [], "LOC": []}

            # Common person names
            person_patterns = [
                r'\b(?:Mr|Ms|Mrs|Dr|Prof)\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:said|announced|reported|stated)\b'
            ]

            # Common organization indicators
            org_patterns = [
                r'\b([A-Z][a-zA-Z&\s]+(?:Inc|Corp|Ltd|LLC|Co|Company|Bank|University|Institute))\b',
                r'\b([A-Z][a-zA-Z\s]+)\s+(?:announced|reported|stated|declared)\b'
            ]

            # Location patterns
            loc_patterns = [
                r'\b(?:in|from|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
                r'\b([A-Z][a-z]+)\s+(?:city|country|state|region|district)\b'
            ]

            # Extract persons
            for pattern in person_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if match not in parsed["PERSON"] and len(match) > 2:
                        parsed["PERSON"].append(match)

            # Extract organizations
            for pattern in org_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if match not in parsed["ORG"] and len(match) > 2:
                        parsed["ORG"].append(match[:50])  # Limit length

            # Extract locations
            for pattern in loc_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if match not in parsed["LOC"] and len(match) > 2:
                        parsed["LOC"].append(match)

            # If no entities found, extract capitalized words as potential entities
            if not any(parsed.values()):
                capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', text)
                if capitalized:
                    # Distribute them across categories
                    for i, word in enumerate(set(capitalized)[:5]):
                        if i % 3 == 0:
                            parsed["PERSON"].append(word)
                        elif i % 3 == 1:
                            parsed["ORG"].append(word)
                        else:
                            parsed["LOC"].append(word)

            return parsed
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return {"PERSON": [], "ORG": [], "LOC": []}

    async def detect_toxicity(self, text: str) -> dict:
        """Detect toxic content using zero-shot"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: self.zero_shot(
                    text[:512],
                    ["toxic", "clean"],
                    multi_class=False
                )
            )

            toxic_score = 0
            for label, score in zip(result['labels'], result['scores']):
                if label == 'toxic':
                    toxic_score = score
                    break

            is_toxic = toxic_score > 0.5
            return {
                "is_toxic": is_toxic,
                "toxicity_score": round(toxic_score * 100, 1),
                "label": "NSFW" if is_toxic else "CLEAN"
            }
        except Exception as e:
            logger.error(f"Toxicity detection error: {e}")
            return {"is_toxic": False, "toxicity_score": 0, "label": "CLEAN"}

    async def classify_misinformation(self, text: str) -> dict:
        """Classify misinformation risk"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: self.zero_shot(
                    text[:512],
                    ["misinformation", "credible"],
                    multi_class=False
                )
            )

            misinfo_score = 0
            for label, score in zip(result['labels'], result['scores']):
                if label == 'misinformation':
                    misinfo_score = score
                    break

            return {
                "misinformation_likelihood": round(misinfo_score * 100, 1),
                "risk_level": "high" if misinfo_score > 0.6 else "low"
            }
        except Exception as e:
            logger.error(f"Misinformation classification error: {e}")
            return {"misinformation_likelihood": 0, "risk_level": "low"}

    async def detect_propaganda(self, text: str) -> dict:
        """Detect propaganda"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: self.zero_shot(
                    text[:512],
                    ["propaganda", "neutral"],
                    multi_class=False
                )
            )

            prop_score = 0
            for label, score in zip(result['labels'], result['scores']):
                if label == 'propaganda':
                    prop_score = score
                    break

            return {
                "propaganda_detected": prop_score > 0.6,
                "propaganda_score": round(prop_score * 100, 1)
            }
        except Exception as e:
            logger.error(f"Propaganda detection error: {e}")
            return {"propaganda_detected": False, "propaganda_score": 0}

    async def detect_offensive_language(self, text: str) -> dict:
        """Detect offensive language"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: self.zero_shot(
                    text[:512],
                    ["offensive", "appropriate"],
                    multi_class=False
                )
            )

            offensive_score = 0
            for label, score in zip(result['labels'], result['scores']):
                if label == 'offensive':
                    offensive_score = score
                    break

            return {
                "is_offensive": offensive_score > 0.6,
                "offensive_score": round(offensive_score * 100, 1)
            }
        except Exception as e:
            logger.error(f"Offensive language detection error: {e}")
            return {"is_offensive": False, "offensive_score": 0}

# Initialize models (downloads on first run)
logger.info("Starting local ML model initialization...")
local_models = LocalMLModels()
