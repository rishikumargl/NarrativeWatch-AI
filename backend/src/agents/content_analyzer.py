"""Content Analyzer Agent for NarrativeWatch AI."""

from typing import Dict, Any, List
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent
from src.utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class ContentAnalyzerAgent(BaseAgent):
    """Analyze Twitter tweet content and extract features."""

    def __init__(self):
        """Initialize Content Analyzer Agent."""
        super().__init__(
            name="Content Analyzer",
            description="Extract and classify tweet content for emotional language, "
                       "narrative themes, hashtag patterns, mention patterns, and engagement metrics"
        )
        self.text_processor = TextProcessor()

    def run(self, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Twitter tweet content.

        Args:
            tweet_data: Dict with text, hashtags, mentions, comments, etc.

        Returns:
            Dict with analysis results
        """
        try:
            if not self.validate_input(tweet_data):
                return {"status": "error", "message": "Invalid input data"}

            text = tweet_data.get("text", "")
            hashtags = tweet_data.get("hashtags", [])
            mentions = tweet_data.get("mentions", [])
            replies = tweet_data.get("replies", [])
            posting_time = tweet_data.get("created_at")
            engagement_data = tweet_data.get("engagement", {})

            analysis = {
                "emotional_language": self._analyze_emotional_language(text, replies),
                "narrative_themes": self._analyze_narrative_themes(text, replies),
                "hashtag_patterns": self._analyze_hashtag_patterns(hashtags),
                "mention_patterns": self._analyze_mention_patterns(mentions),
                "posting_pattern": self._analyze_posting_pattern(posting_time),
                "engagement_metrics": self._analyze_engagement_metrics(engagement_data),
                "text_patterns": self._analyze_text_patterns(text),
            }

            return {
                "status": "success",
                "agent": "Twitter Content Analyzer",
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

    def _analyze_emotional_language(self, text: str, replies: List[str]) -> Dict[str, Any]:
        """Analyze emotional language in tweet."""
        all_text = text + " " + " ".join(replies)

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

    def _analyze_narrative_themes(self, text: str, replies: List[str]) -> List[str]:
        """Identify narrative themes in tweet."""
        all_text = (text + " " + " ".join(replies)).lower()

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

    def _analyze_mention_patterns(self, mentions: List[str]) -> Dict[str, Any]:
        """Analyze mention patterns and influencer targeting."""
        if not mentions:
            return {
                "total_mentions": 0,
                "unique_mentions": 0,
                "mention_frequency": {},
                "mention_types": {},
            }

        from collections import Counter
        mention_counts = Counter(mentions)

        # Categorize mentions
        mention_types = {
            "official": [],  # Official accounts (verified)
            "influencer": [],  # Influential accounts
            "peer": [],  # Regular user accounts
            "bot": [],  # Automated accounts
        }

        return {
            "total_mentions": len(mentions),
            "unique_mentions": len(set(mentions)),
            "mention_frequency": dict(mention_counts.most_common(10)),
            "mention_types": mention_types,
            "network_effect": len(set(mentions)) / max(1, len(mentions)),
        }

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
