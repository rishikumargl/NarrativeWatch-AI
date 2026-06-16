"""Cross-source verification service to check multiple news outlets for same story."""

import logging
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
import os
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class CrossSourceVerification:
    """Verify stories by checking multiple news sources."""

    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")

        if not self.newsapi_key and not self.tavily_key:
            logger.warning("⚠️ Neither NEWSAPI_KEY nor TAVILY_API_KEY set - cross-source verification disabled")
        elif self.newsapi_key:
            logger.info("✅ Using NewsAPI for cross-source verification (Tavily as fallback)")
        else:
            logger.info("✅ Using Tavily for cross-source verification (NewsAPI not available)")

    async def verify_story(self, title: str, url: str, keywords: List[str], article_content: str = None) -> Dict:
        """Verify a story by searching multiple news sources.

        Args:
            title: Article title
            url: Original article URL
            keywords: Key terms to search for (entities, main topics)

        Returns:
            Dictionary with verification results
        """

        logger.info(f"🔍 Starting cross-source verification for: {title[:50]}...")

        if not self.newsapi_key and not self.tavily_key:
            logger.warning("Cannot verify - Neither NewsAPI nor Tavily keys available")
            return self._empty_verification()

        try:
            # Extract domain from URL
            from urllib.parse import urlparse
            source_domain = urlparse(url).netloc.replace("www.", "")

            # Use main keywords for search
            search_query = " AND ".join(keywords[:3]) if keywords else title[:100]

            logger.info(f"📰 Searching with query: {search_query}")

            # Try NewsAPI first, fallback to Tavily
            similar_articles = None
            if self.newsapi_key:
                logger.info("🔍 Trying NewsAPI...")
                similar_articles = await self._search_newsapi(search_query, source_domain)

            # Fallback to Tavily if NewsAPI fails or not available
            if not similar_articles and self.tavily_key:
                logger.warning("📡 NewsAPI failed/unavailable, falling back to Tavily...")
                similar_articles = await self._search_tavily(search_query, source_domain)

            # Default to empty list if both fail
            if similar_articles is None:
                similar_articles = []

            # Analyze results with content similarity
            verification = self._analyze_verification(
                title=title,
                source_domain=source_domain,
                similar_articles=similar_articles,
                keywords=keywords,
                original_content=article_content
            )

            logger.info(f"✅ Verification complete: {verification['confidence_score']}% confident")
            return verification

        except Exception as e:
            logger.error(f"❌ Cross-source verification failed: {str(e)}")
            return self._empty_verification()

    async def _search_newsapi(self, query: str, exclude_domain: str) -> List[Dict]:
        """Search NewsAPI for similar articles.

        Args:
            query: Search query
            exclude_domain: Domain to exclude (original source)

        Returns:
            List of similar articles
        """
        try:
            url = "https://newsapi.org/v2/everything"

            # Search parameters
            params = {
                "q": query,
                "sortBy": "relevancy",
                "language": "en",
                "apiKey": self.newsapi_key,
                "pageSize": 10,  # Get top 10 results
                "from": (datetime.utcnow() - timedelta(days=7)).isoformat(),  # Last 7 days
            }

            logger.info(f"📡 Calling NewsAPI with query: {query}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get("articles", [])

                        # Filter out the original source
                        filtered = [
                            a for a in articles
                            if exclude_domain.lower() not in a.get("source", {}).get("name", "").lower()
                        ]

                        logger.info(f"📰 Found {len(filtered)} articles from other sources")
                        return filtered[:5]  # Return top 5
                    else:
                        logger.error(f"❌ NewsAPI error: {response.status}")
                        return []

        except aiohttp.ClientError as e:
            logger.error(f"⚠️ Network error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"❌ Search failed: {str(e)}")
            return []

    async def _search_tavily(self, query: str, exclude_domain: str) -> List[Dict]:
        """Search Tavily for similar articles (fallback).

        Args:
            query: Search query
            exclude_domain: Domain to exclude (original source)

        Returns:
            List of similar articles
        """
        try:
            url = "https://api.tavily.com/search"

            payload = {
                "api_key": self.tavily_key,
                "query": query,
                "include_domains": [],
                "exclude_domains": [exclude_domain],
                "max_results": 10,
            }

            logger.info(f"📡 Calling Tavily with query: {query}")

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])

                        # Convert Tavily format to similar format as NewsAPI
                        articles = []
                        for result in results:
                            articles.append({
                                "source": {"name": result.get("source", "Unknown")},
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "publishedAt": datetime.now(timezone.utc).isoformat(),
                                "description": result.get("content", "")
                            })

                        logger.info(f"📰 Tavily found {len(articles)} articles")
                        return articles[:5]
                    else:
                        logger.error(f"❌ Tavily error: {response.status}")
                        return []

        except aiohttp.ClientError as e:
            logger.error(f"⚠️ Tavily network error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"❌ Tavily search failed: {str(e)}")
            return []

    def _analyze_verification(
        self,
        title: str,
        source_domain: str,
        similar_articles: List[Dict],
        keywords: List[str],
        original_content: str = None
    ) -> Dict:
        """Analyze verification results.

        Args:
            title: Original article title
            source_domain: Original source domain
            similar_articles: Articles found from other sources
            keywords: Search keywords

        Returns:
            Verification analysis
        """

        logger.info(f"📊 Analyzing verification: {len(similar_articles)} articles found")
        verification_score = 0
        matching_sources = []
        verification_details = []

        # Check 1: Multiple sources reporting same story
        if similar_articles:
            verification_score += 30
            for article in similar_articles:
                source_name = article.get("source", {}).get("name", "Unknown")
                matching_sources.append({
                    "source": source_name,
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "description": article.get("description", "")[:200]
                })
            verification_details.append(f"✅ Found {len(similar_articles)} corroborating articles from other sources")

        # Check 2: Reputable sources
        reputable_sources = ["bbc", "reuters", "ap news", "times of india", "bloomberg", "the guardian"]
        has_reputable = any(
            any(rep in source["source"].lower() for rep in reputable_sources)
            for source in matching_sources
        )
        if has_reputable:
            verification_score += 25
            verification_details.append("✅ Story covered by reputable news outlets")

        # Check 3: Recent articles (within last 24 hours)
        recent_count = 0
        now_utc = datetime.now(timezone.utc)
        for article in similar_articles:
            try:
                pub_date_str = article.get("publishedAt", "")
                if pub_date_str:
                    try:
                        # Try ISO format first
                        if "T" in pub_date_str:
                            pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                        else:
                            # Try other common formats
                            from dateutil import parser as date_parser
                            pub_date = date_parser.parse(pub_date_str)

                        # Ensure both are timezone-aware for comparison
                        if pub_date.tzinfo is None:
                            pub_date = pub_date.replace(tzinfo=timezone.utc)

                        # Safe comparison
                        if now_utc.tzinfo is None:
                            now_utc = now_utc.replace(tzinfo=timezone.utc)

                        time_diff = (now_utc - pub_date).days
                        if time_diff <= 1 and time_diff >= 0:
                            recent_count += 1
                    except Exception as parse_error:
                        logger.debug(f"Could not parse date '{pub_date_str}': {parse_error}")
                        continue
            except Exception as e:
                logger.debug(f"Error processing article date: {e}")
                continue

        if recent_count > 0:
            verification_score += 20
            verification_details.append(f"✅ Story reported by {recent_count} sources in last 24 hours")

        # Check 4: Multiple matching keywords + Content similarity
        keyword_matches = 0
        content_similarity_scores = []

        for article in similar_articles:
            article_text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            for keyword in keywords[:3]:
                if keyword.lower() in article_text:
                    keyword_matches += 1

            # Check content similarity if we have original content
            if original_content and article.get('description'):
                similarity = self._calculate_similarity(
                    original_content,
                    article.get('description', '')
                )
                content_similarity_scores.append(similarity)
                if similarity > 0.5:  # 50% similarity threshold
                    logger.debug(f"📝 High content similarity ({similarity:.0%}) with {article.get('source', {}).get('name', 'Unknown')}")

        # Boost score if content is highly similar
        if content_similarity_scores:
            avg_similarity = sum(content_similarity_scores) / len(content_similarity_scores)
            if avg_similarity > 0.6:
                verification_score += 20
                verification_details.append(f"✅ Content highly similar to {len([s for s in content_similarity_scores if s > 0.5])} other sources")

        if keyword_matches > 0:
            verification_score += min(25, keyword_matches * 5)
            try:
                unique_sources = len(set(
                    a.get('source', {}).get('name', 'Unknown')
                    for a in similar_articles
                ))
                verification_details.append(f"✅ Key entities found in {unique_sources} sources")
            except Exception as e:
                logger.debug(f"Could not count sources: {e}")
                verification_details.append(f"✅ Key entities found in multiple sources")

        # Determine confidence level
        if verification_score >= 75:
            confidence_level = "VERY HIGH"
        elif verification_score >= 50:
            confidence_level = "HIGH"
        elif verification_score >= 25:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        return {
            "verified": verification_score >= 50,
            "confidence_score": verification_score,
            "confidence_level": confidence_level,
            "matching_sources": matching_sources,
            "verification_details": verification_details,
            "total_sources_reporting": len(matching_sources),
            "recommendation": self._get_recommendation(verification_score, len(matching_sources))
        }

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)."""
        try:
            # Normalize texts
            t1 = text1.lower()[:500] if text1 else ""
            t2 = text2.lower()[:500] if text2 else ""

            # Use SequenceMatcher for similarity
            matcher = SequenceMatcher(None, t1, t2)
            return matcher.ratio()
        except Exception as e:
            logger.debug(f"Could not calculate similarity: {e}")
            return 0.0

    def _get_recommendation(self, score: int, num_sources: int) -> str:
        """Generate recommendation based on verification score.

        Args:
            score: Verification score (0-100)
            num_sources: Number of matching sources

        Returns:
            Recommendation text
        """

        if score >= 75 and num_sources >= 3:
            return "✅ VERIFIED: Story is reported by multiple reputable sources. Safe to share."
        elif score >= 50 and num_sources >= 2:
            return "🟡 LIKELY TRUE: Story is covered by other sources but verification could be stronger."
        elif score >= 25:
            return "⚠️ UNVERIFIED: Limited coverage from other sources. Verify with official statements."
        else:
            return "❌ UNCONFIRMED: Story not found in other major news sources. May be false or too new."

    def _empty_verification(self) -> Dict:
        """Return empty verification when API unavailable."""
        message = "⚠️ Cross-source verification unavailable"
        recommendation = "Add NewsAPI or Tavily API key to .env to enable verification"

        return {
            "verified": False,
            "confidence_score": 0,
            "confidence_level": "UNAVAILABLE",
            "matching_sources": [],
            "verification_details": [message],
            "total_sources_reporting": 0,
            "recommendation": recommendation
        }


# Initialize service
cross_source_verification = CrossSourceVerification()
