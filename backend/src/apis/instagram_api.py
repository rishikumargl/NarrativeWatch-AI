"""Instagram Graph API wrapper for data collection."""

import os
import logging
from typing import Optional, List, Dict, Any
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class InstagramAPI:
    """Wrapper for Instagram Graph API for data collection."""

    def __init__(self, access_token: Optional[str] = None):
        """Initialize Instagram API client.

        Args:
            access_token: Instagram Graph API access token.
                         If None, reads from INSTAGRAM_ACCESS_TOKEN env var.
        """
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN environment variable not set")

        self.base_url = "https://graph.instagram.com/v18.0"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        logger.info("[OK] Instagram API client initialized")

    def _make_request(
        self, endpoint: str, method: str = "GET", params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request.

        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters

        Returns:
            Response data
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram API error: {e}")
            return {"error": str(e)}

    def get_page(self, username: str) -> Dict[str, Any]:
        """Get Instagram page info by username.

        Args:
            username: Instagram username

        Returns:
            Page information
        """
        logger.info(f"Fetching page: {username}")

        # Get user ID from username
        params = {
            "user_id": username,
            "fields": "id,username,name,biography,website,profile_picture_url,follower_count,media_count",
        }

        return self._make_request(f"/{username}", params=params)

    def get_page_posts(
        self, username: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Get recent posts from a page.

        Args:
            username: Instagram username
            limit: Number of posts to retrieve

        Returns:
            Posts from the page
        """
        logger.info(f"Fetching posts for: {username} (limit: {limit})")

        params = {
            "fields": "id,caption,media_type,media_url,timestamp,like_count,comments_count",
            "limit": min(limit, 50),  # Cap at 50
        }

        return self._make_request(f"/{username}/media", params=params)

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get detailed information about a post.

        Args:
            post_id: Instagram post ID

        Returns:
            Post details
        """
        logger.info(f"Fetching post: {post_id}")

        params = {
            "fields": "id,caption,media_type,media_url,timestamp,like_count,comments_count,engagement"
        }

        return self._make_request(f"/{post_id}", params=params)

    def get_post_comments(
        self, post_id: str, limit: int = 20
    ) -> Dict[str, Any]:
        """Get comments on a post.

        Args:
            post_id: Instagram post ID
            limit: Number of comments to retrieve

        Returns:
            Comments on the post
        """
        logger.info(f"Fetching comments for post: {post_id} (limit: {limit})")

        params = {
            "fields": "id,from{username},text,timestamp,like_count",
            "limit": min(limit, 100),
        }

        return self._make_request(f"/{post_id}/comments", params=params)

    def get_page_followers(self, username: str) -> Dict[str, Any]:
        """Get follower count for a page.

        Args:
            username: Instagram username

        Returns:
            Follower information
        """
        logger.info(f"Fetching follower count for: {username}")

        return self.get_page(username)

    def search_hashtag(self, hashtag: str) -> Dict[str, Any]:
        """Search for hashtag information.

        Args:
            hashtag: Hashtag to search (without #)

        Returns:
            Hashtag information
        """
        logger.info(f"Searching hashtag: {hashtag}")

        params = {
            "user_id": hashtag,
            "fields": "id,name",
        }

        return self._make_request(f"/ig_hashtag_search", params=params)

    def get_hashtag_recent_posts(
        self, hashtag_id: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Get recent posts with a hashtag.

        Args:
            hashtag_id: Hashtag ID from search
            limit: Number of posts to retrieve

        Returns:
            Posts with the hashtag
        """
        logger.info(f"Fetching posts for hashtag: {hashtag_id}")

        params = {
            "fields": "id,caption,media_type,timestamp",
            "limit": min(limit, 50),
        }

        return self._make_request(f"/{hashtag_id}/recent_media", params=params)

    def check_health(self) -> bool:
        """Check if API is working.

        Returns:
            True if API is accessible
        """
        try:
            response = self.session.get(f"{self.base_url}/me", timeout=10)
            is_healthy = response.status_code == 200
            logger.info(f"{'[OK]' if is_healthy else '[FAIL]'} Instagram API health: {response.status_code}")
            return is_healthy
        except Exception as e:
            logger.error(f"Instagram API health check failed: {e}")
            return False

    def rate_limit_status(self) -> Dict[str, Any]:
        """Get rate limit status.

        Returns:
            Rate limit information
        """
        headers = self.session.head(f"{self.base_url}/me").headers
        return {
            "limit": headers.get("x-rate-limit-limit"),
            "remaining": headers.get("x-rate-limit-remaining"),
            "reset": headers.get("x-rate-limit-reset"),
        }
