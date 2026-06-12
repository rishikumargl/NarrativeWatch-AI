"""Content Analyzer Agent for NarrativeWatch AI."""

from typing import Dict, Any, List
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent
from src.utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class ContentAnalyzerAgent(BaseAgent):
    """Analyze news article content and extract features."""

    def __init__(self):
        """Initialize Content Analyzer Agent."""
        super().__init__(
            name="Content Analyzer",
            description="Extract and classify article content for emotional language, "
                       "narrative themes, factual claims, source credibility, and writing patterns"
        )
        self.text_processor = TextProcessor()

    def run(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze news article content.

        Args:
            article_data: Dict with title, content, source, author, etc.

        Returns:
            Dict with analysis results
        """
        try:
            if not self.validate_input(article_data):
                return {"status": "error", "message": "Invalid input data"}

            title = article_data.get("title", "")
            content = article_data.get("content", "")
            description = article_data.get("description", "")
            source = article_data.get("source", "")
            author = article_data.get("author", "")
            published_at = article_data.get("published_at")

            full_text = f"{title} {description} {content}"

            analysis = {
                "emotional_language": self._analyze_emotional_language(full_text),
                "narrative_themes": self._analyze_narrative_themes(full_text),
                "source_credibility": self._analyze_source_credibility(source, author),
                "factual_claims": self._analyze_factual_claims(content),
                "writing_patterns": self._analyze_writing_patterns(title, content),
                "text_patterns": self._analyze_text_patterns(full_text),
            }

            return {
                "status": "success",
                "agent": "News Content Analyzer",
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Content Analyzer error: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def validate_input(self, input_data: Any) -> bool:
        """Validate input data."""
        if not isinstance(input_data, dict):
            return False
        if "caption" not in input_data:
            return False
        return True

    def _analyze_emotional_language(self, text: str) -> Dict[str, Any]:
        """Analyze emotional language in article."""
        all_text = text

        sentiment = self.text_processor.calculate_sentiment(all_text)
        subjectivity = self.text_processor.calculate_subjectivity(all_text)
        emotional_intensity = self.text_processor.analyze_emotional_intensity(all_text)

        # Classify sentiment
        if sentiment > 0.2:
            sentiment_class = "positive"
        elif sentiment < -0.2:
            sentiment_class = "negative"
        else:
            sentiment_class = "neutral"

        return {
            "sentiment": {
                "polarity": float(sentiment),
                "classification": sentiment_class,
            },
            "subjectivity": float(subjectivity),
            "emotional_intensity": emotional_intensity,
            "overall_tone": self._determine_tone(sentiment, emotional_intensity),
        }

    def _analyze_narrative_themes(self, text: str) -> List[str]:
        """Identify narrative themes in article."""
        all_text = text.lower()

        themes = []
        theme_patterns = {
            "conspiracy": [
                "conspiracy", "cover up", "hidden truth", "shadow government",
                "deep state", "illuminati", "exposed"
            ],
            "propaganda": [
                "propaganda", "brainwash", "indoctrination", "misinformation",
                "false narrative", "fake news"
            ],
            "sensationalism": [
                "shocking", "unbelievable", "you won't believe", "must watch",
                "insane", "crazy", "viral"
            ],
            "political": [
                "vote", "election", "campaign", "party", "political",
                "democrat", "republican", "liberal", "conservative"
            ],
            "health": [
                "health", "disease", "cure", "medicine", "vaccine",
                "doctors", "symptoms", "treatment"
            ],
            "entertainment": [
                "celebrity", "actor", "movie", "show", "music",
                "entertainment", "viral", "funny"
            ],
            "lifestyle": [
                "fashion", "beauty", "lifestyle", "trends", "style",
                "makeup", "outfit", "aesthetic"
            ],
            "social_justice": [
                "justice", "equality", "discrimination", "racism", "rights",
                "marginalized", "oppression", "systemic"
            ],
        }

        for theme, keywords in theme_patterns.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)

        return themes

    def _analyze_hashtag_patterns(self, hashtags: List[str]) -> Dict[str, Any]:
        """Analyze hashtag patterns and frequency."""
        if not hashtags:
            return {
                "total_hashtags": 0,
                "unique_hashtags": 0,
                "hashtag_frequency": {},
                "trending_indicators": [],
            }

        from collections import Counter
        hashtag_counts = Counter(hashtags)

        # Detect trending hashtags (assumed to be common ones)
        trending = [tag for tag, count in hashtag_counts.items() if count > 1]

        return {
            "total_hashtags": len(hashtags),
            "unique_hashtags": len(set(hashtags)),
            "hashtag_frequency": dict(hashtag_counts.most_common(10)),
            "trending_indicators": trending,
            "hashtag_categories": self._categorize_hashtags(hashtags),
        }

    def _analyze_source_credibility(self, source: str, author: str) -> Dict[str, Any]:
        """Analyze news source and author credibility."""
        credibility_score = 0.5  # Default neutral

        # Check source reputation
        reputable_sources = {
            "BBC", "Reuters", "AP News", "The Guardian", "NPR",
            "Associated Press", "Deutsche Welle", "Agence France-Presse",
            "The New York Times", "The Washington Post"
        }

        suspicious_indicators = [
            "fake", "hoax", "satire", "scam", "fraud",
            "conspiracy", "exposed", "coverup"
        ]

        if any(src in source for src in reputable_sources):
            credibility_score += 0.2

        if any(indicator in source.lower() for indicator in suspicious_indicators):
            credibility_score -= 0.3

        author_present = bool(author and author.strip())
        if author_present:
            credibility_score += 0.1

        return {
            "source": source,
            "credibility_score": min(1.0, max(0.0, credibility_score)),
            "author_present": author_present,
            "is_reputable_source": any(src in source for src in reputable_sources),
            "confidence": "medium",
        }

    def _analyze_factual_claims(self, content: str) -> Dict[str, Any]:
        """Analyze potential factual claims in article."""
        claims = {
            "total_sentences": 0,
            "sentences_with_numbers": 0,
            "sentences_with_quotes": 0,
            "sentences_with_assertions": 0,
            "has_sources": False,
            "has_evidence": False,
        }

        sentences = [s.strip() for s in content.split(".") if s.strip()]
        claims["total_sentences"] = len(sentences)

        import re
        for sentence in sentences:
            # Check for numbers (statistics, dates)
            if re.search(r"\d+", sentence):
                claims["sentences_with_numbers"] += 1

            # Check for quotes
            if '"' in sentence or "'" in sentence:
                claims["sentences_with_quotes"] += 1

            # Check for assertion patterns
            if any(word in sentence.lower() for word in ["said", "stated", "reported", "found", "showed"]):
                claims["sentences_with_assertions"] += 1

        # Check for sources/references
        if "source" in content.lower() or "according to" in content.lower():
            claims["has_sources"] = True

        if "study" in content.lower() or "research" in content.lower():
            claims["has_evidence"] = True

        return claims

    def _analyze_writing_patterns(self, title: str, content: str) -> Dict[str, Any]:
        """Analyze writing style and patterns."""
        patterns = {
            "title_length": len(title.split()),
            "content_length": len(content.split()),
            "avg_word_length": 0.0,
            "has_exclamation": "!" in title or "!" in content,
            "has_questions": "?" in title or "?" in content,
            "sensational_indicators": [],
        }

        # Calculate average word length
        all_words = (title + " " + content).split()
        if all_words:
            patterns["avg_word_length"] = sum(len(w) for w in all_words) / len(all_words)

        # Check for sensational language
        sensational = [
            "shocking", "unbelievable", "you won't believe",
            "secret", "exposed", "must read", "breaking",
            "exclusive", "amazing", "terrible"
        ]

        for word in sensational:
            if word in (title + " " + content).lower():
                patterns["sensational_indicators"].append(word)

        return patterns

    def _categorize_hashtags(self, hashtags: List[str]) -> Dict[str, List[str]]:
        """Categorize hashtags by type."""
        categories = {
            "branded": [],
            "trending": [],
            "niche": [],
            "location": [],
        }

        for tag in hashtags:
            tag_lower = tag.lower()
            # Simple categorization based on patterns
            if any(term in tag_lower for term in ["location", "city", "place", "area"]):
                categories["location"].append(tag)
            elif tag_lower in ["trending", "viral", "foryou", "explore"]:
                categories["trending"].append(tag)
            elif len(tag) > 15:
                categories["niche"].append(tag)
            else:
                categories["branded"].append(tag)

        return {k: v for k, v in categories.items() if v}

    def _analyze_posting_pattern(self, posting_time: Any) -> Dict[str, Any]:
        """Analyze posting timing and pattern."""
        pattern = {
            "frequency": "unknown",
            "consistency": 0.0,
            "timing_pattern": "unknown",
            "optimal_time": self._determine_optimal_time(),
        }

        if posting_time:
            try:
                from datetime import datetime
                post_dt = datetime.fromisoformat(str(posting_time))
                hour = post_dt.hour

                # Determine time of day
                if 6 <= hour < 12:
                    pattern["timing_pattern"] = "morning"
                elif 12 <= hour < 18:
                    pattern["timing_pattern"] = "afternoon"
                elif 18 <= hour < 24:
                    pattern["timing_pattern"] = "evening"
                else:
                    pattern["timing_pattern"] = "night"

            except Exception as e:
                logger.warning(f"Could not parse posting time: {e}")

        return pattern

    def _analyze_engagement_metrics(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze engagement metrics."""
        return {
            "likes": engagement_data.get("likes", 0),
            "comments": engagement_data.get("comments", 0),
            "shares": engagement_data.get("shares", 0),
            "engagement_rate": engagement_data.get("engagement_rate", 0.0),
            "engagement_quality": self._assess_engagement_quality(engagement_data),
        }

    def _analyze_text_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze text patterns and features."""
        patterns = self.text_processor.extract_patterns(text)

        return {
            "language_features": patterns.get("language_features", {}),
            "named_entities": patterns.get("named_entities", {}),
            "readability": self.text_processor.analyze_readability(text),
            "word_frequency": self.text_processor.get_word_frequency(text, top_n=5),
        }

    def _determine_tone(self, sentiment: float, emotional_intensity: Dict[str, float]) -> str:
        """Determine overall tone of content."""
        if emotional_intensity.get("excitement", 0) > 0.3:
            return "enthusiastic"
        elif emotional_intensity.get("anger", 0) > 0.2:
            return "hostile"
        elif emotional_intensity.get("sadness", 0) > 0.2:
            return "melancholic"
        elif sentiment > 0.5:
            return "positive"
        elif sentiment < -0.5:
            return "negative"
        else:
            return "neutral"

    def _determine_optimal_time(self) -> str:
        """Determine optimal posting time."""
        return "afternoon"  # General default

    def _assess_engagement_quality(self, engagement_data: Dict[str, Any]) -> str:
        """Assess quality of engagement."""
        engagement_rate = engagement_data.get("engagement_rate", 0)

        if engagement_rate >= 0.05:
            return "high"
        elif engagement_rate > 0.02:
            return "medium"
        else:
            return "low"
