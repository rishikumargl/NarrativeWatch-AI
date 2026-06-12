"""NewsAPI client for fetching news articles."""

import os
import logging
from typing import Dict, List, Any, Optional
import requests

logger = logging.getLogger(__name__)


class NewsAPIClient:
    """Client for interacting with NewsAPI.org (Free tier)."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        """Initialize NewsAPI client with API key from environment."""
        self.api_key = os.getenv("NEWSAPI_KEY", "")
        self.session = requests.Session()

        if not self.api_key:
            logger.warning(
                "NEWSAPI_KEY not found. Get free key at https://newsapi.org/"
            )
        else:
            logger.info("[OK] NewsAPI client initialized")

    def search_articles(
        self,
        query: str,
        num_articles: int = 10,
        sort_by: str = "publishedAt",
        language: str = "en",
    ) -> List[Dict[str, Any]]:
        """
        Search for news articles by query.

        Args:
            query: Search keywords/topics
            num_articles: Number of articles to fetch (max 100)
            sort_by: Sort order (relevancy, popularity, publishedAt)
            language: Language code (e.g., en, es, fr)

        Returns:
            List of articles with metadata
        """
        try:
            if not self.api_key:
                logger.error("NEWSAPI_KEY not configured")
                return []

            endpoint = f"{self.BASE_URL}/everything"
            params = {
                "q": query,
                "sortBy": sort_by,
                "language": language,
                "pageSize": min(num_articles, 100),
                "apiKey": self.api_key,
            }

            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = []

            if data.get("status") == "ok":
                for article in data.get("articles", []):
                    articles.append(self._parse_article(article))
                logger.info(f"Found {len(articles)} articles for query: {query}")
            else:
                logger.warning(f"NewsAPI error: {data.get('message', 'Unknown error')}")

            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching articles: {e}")
            return []

    def get_top_headlines(
        self,
        category: str = "general",
        country: str = "us",
        num_articles: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get top headlines by category and country.

        Args:
            category: News category (business, entertainment, general, health, science, sports, technology)
            country: Country code (us, gb, ca, etc.)
            num_articles: Number of articles to fetch

        Returns:
            List of headline articles
        """
        try:
            if not self.api_key:
                return []

            endpoint = f"{self.BASE_URL}/top-headlines"
            params = {
                "category": category,
                "country": country,
                "pageSize": min(num_articles, 100),
                "apiKey": self.api_key,
            }

            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = []

            if data.get("status") == "ok":
                for article in data.get("articles", []):
                    articles.append(self._parse_article(article))
                logger.info(f"Found {len(articles)} headlines for {category}/{country}")
            else:
                logger.warning(f"NewsAPI error: {data.get('message', 'Unknown error')}")

            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching headlines: {e}")
            return []

    def _parse_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw article data into standard format."""
        return {
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "content": article.get("content", ""),
            "source": article.get("source", {}).get("name", "Unknown"),
            "author": article.get("author", ""),
            "published_at": article.get("publishedAt", ""),
            "url": article.get("url", ""),
            "image_url": article.get("urlToImage", ""),
        }

    def extract_keywords(self, text: str) -> List[str]:
        """Extract potential keywords from article text."""
        import re

        # Simple keyword extraction: words > 4 chars, excluding common words
        stopwords = {
            "the", "this", "that", "with", "from", "have", "will", "your",
            "which", "about", "than", "does", "their", "been", "would", "more"
        }

        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [
            w for w in set(words)
            if len(w) > 4 and w not in stopwords
        ]
        return sorted(keywords)[:10]

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from article text.
        Uses simple pattern matching without NLP libraries.
        """
        import re

        entities = {
            "potential_people": [],
            "potential_organizations": [],
            "potential_locations": [],
            "hashtags": [],
        }

        # Extract capitalized proper nouns (simple heuristic)
        capitalized = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        if capitalized:
            entities["potential_people"] = list(set(capitalized))[:5]

        # Extract hashtags
        hashtags = re.findall(r"#\w+", text)
        if hashtags:
            entities["hashtags"] = list(set(hashtags))

        return {k: v for k, v in entities.items() if v}

    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article structure and content.

        Returns statistics about the article.
        """
        title = article.get("title", "")
        content = article.get("content", "")
        description = article.get("description", "")

        full_text = f"{title} {description} {content}"

        # Basic statistics
        word_count = len(full_text.split())
        sentence_count = len([s for s in full_text.split(".") if s.strip()])

        # Extract data
        keywords = self.extract_keywords(full_text)
        entities = self.extract_entities(full_text)

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "keywords": keywords,
            "entities": entities,
            "has_image": bool(article.get("image_url")),
            "author_present": bool(article.get("author")),
            "source": article.get("source", "unknown"),
        }

    def detect_misinformation_signals(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential misinformation signals in article.

        Returns dict with signal types and scores.
        """
        title = article.get("title", "")
        content = article.get("content", "")
        source = article.get("source", "")

        signals = {
            "sensationalism_score": 0.0,
            "no_author_flag": False,
            "suspicious_source": False,
            "all_caps_title": False,
            "excessive_punctuation": False,
            "missing_evidence": False,
        }

        # Check for sensational language
        sensational_words = [
            "shocking", "unbelievable", "you won't believe",
            "experts hate", "secret", "exposed", "must see"
        ]
        sensational_count = sum(
            1 for word in sensational_words if word in title.lower()
        )
        signals["sensationalism_score"] = min(1.0, sensational_count * 0.3)

        # Check for missing author
        if not article.get("author"):
            signals["no_author_flag"] = True

        # Check for all caps titles
        title_words = title.split()
        caps_ratio = sum(1 for w in title_words if w.isupper()) / max(1, len(title_words))
        if caps_ratio > 0.3:
            signals["all_caps_title"] = True

        # Check for excessive punctuation
        exclamation_count = title.count("!")
        question_count = title.count("?")
        if exclamation_count + question_count > 2:
            signals["excessive_punctuation"] = True

        # Check for missing citations/evidence
        if "?" not in content and "evidence" not in content.lower():
            signals["missing_evidence"] = True

        return signals

    def detect_bias(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential bias indicators in article.

        Returns dict with bias signals.
        """
        title = article.get("title", "")
        content = article.get("content", "")
        source = article.get("source", "")

        bias_signals = {
            "emotional_language_score": 0.0,
            "one_sided": False,
            "opinion_vs_news": False,
            "loaded_language": False,
        }

        # Emotional language indicators
        emotional_words = [
            "terrible", "wonderful", "awful", "amazing",
            "disgusting", "beautiful", "hate", "love"
        ]
        emotional_count = sum(
            1 for word in emotional_words if word in content.lower()
        )
        bias_signals["emotional_language_score"] = min(1.0, emotional_count * 0.15)

        # Check for opinion indicators
        opinion_phrases = [
            "in my opinion", "i believe", "it seems", "apparently",
            "allegedly", "should", "must"
        ]
        opinion_count = sum(
            1 for phrase in opinion_phrases if phrase in content.lower()
        )
        if opinion_count > 3:
            bias_signals["opinion_vs_news"] = True

        # Check for loaded language
        loaded_words = [
            "obviously", "clearly", "undoubtedly", "everyone knows",
            "common sense", "naturally"
        ]
        if any(word in content.lower() for word in loaded_words):
            bias_signals["loaded_language"] = True

        return bias_signals


def get_newsapi_client() -> NewsAPIClient:
    """Get NewsAPI client instance."""
    return NewsAPIClient()
