"""Tavily Search API wrapper for external research."""

import os
import logging
from typing import Optional, List, Dict, Any
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class TavilyAPI:
    """Wrapper for Tavily Search API for external research and fact-finding."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily API client.

        Args:
            api_key: Tavily API key. If None, reads from TAVILY_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")

        self.base_url = "https://api.tavily.com/search"
        self.session = requests.Session()
        logger.info("[OK] Tavily API client initialized")

    def search(
        self,
        query: str,
        max_results: int = 5,
        include_answer: bool = True,
        include_raw_content: bool = False,
    ) -> Dict[str, Any]:
        """Search using Tavily API.

        Args:
            query: Search query
            max_results: Maximum results to return (1-20)
            include_answer: Include AI-generated answer
            include_raw_content: Include raw HTML content

        Returns:
            Dictionary with search results
        """
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": min(max_results, 20),  # Cap at 20
                "include_answer": include_answer,
                "include_raw_content": include_raw_content,
                "topic": "news",  # Focus on news articles
            }

            logger.info(f"Searching Tavily: {query}")
            response = self.session.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"[OK] Found {len(data.get('results', []))} results")

            return {
                "query": query,
                "answer": data.get("answer"),
                "results": data.get("results", []),
                "search_time": datetime.utcnow().isoformat(),
            }

        except requests.exceptions.Timeout:
            logger.error("Tavily search timeout")
            return {"query": query, "error": "Search timeout", "results": []}
        except requests.exceptions.RequestException as e:
            logger.error(f"Tavily search error: {e}")
            return {"query": query, "error": str(e), "results": []}

    def verify_claim(self, claim: str) -> Dict[str, Any]:
        """Verify a specific claim using Tavily.

        Args:
            claim: Claim to verify

        Returns:
            Verification results
        """
        logger.info(f"Verifying claim: {claim}")

        # Search for the claim
        search_results = self.search(
            query=f"verify {claim}",
            max_results=10,
            include_answer=True,
        )

        # Parse results for verification
        results = search_results.get("results", [])
        sources = [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "snippet": r.get("snippet"),
            }
            for r in results[:5]
        ]

        return {
            "claim": claim,
            "answer": search_results.get("answer"),
            "sources": sources,
            "verified": len(sources) > 0,
        }

    def search_hashtag(self, hashtag: str) -> Dict[str, Any]:
        """Search for information about a hashtag or trend.

        Args:
            hashtag: Hashtag or trend to search

        Returns:
            Results about the hashtag
        """
        logger.info(f"Searching hashtag: {hashtag}")

        return self.search(
            query=f"{hashtag} trending",
            max_results=10,
            include_answer=True,
        )

    def search_page_context(self, username: str) -> Dict[str, Any]:
        """Get external context about an Instagram page.

        Args:
            username: Instagram username

        Returns:
            External information about the page
        """
        logger.info(f"Getting context for page: {username}")

        return self.search(
            query=f"{username} instagram account news",
            max_results=5,
            include_answer=True,
        )

    def check_health(self) -> bool:
        """Check if API is working.

        Returns:
            True if API is accessible
        """
        try:
            payload = {
                "api_key": self.api_key,
                "query": "test",
                "max_results": 1,
            }
            response = self.session.post(self.base_url, json=payload, timeout=10)
            is_healthy = response.status_code == 200
            status = "[OK]" if is_healthy else "[FAIL]"
            logger.info(f"{status} Tavily API health: {response.status_code}")
            return is_healthy
        except Exception as e:
            logger.error(f"Tavily API health check failed: {e}")
            return False
