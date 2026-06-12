"""Twitter API client for fetching tweets and user data."""

import os
import logging
from typing import Dict, List, Any, Optional
import tweepy

logger = logging.getLogger(__name__)


class TwitterClient:
    """Client for interacting with Twitter API using tweepy."""

    def __init__(self):
        """Initialize Twitter client with credentials from environment."""
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
        self.api_key = os.getenv("TWITTER_API_KEY", "")
        self.api_secret = os.getenv("TWITTER_API_SECRET", "")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

        self.client = None
        self.api = None

        if self.bearer_token:
            self._init_client_v2()
        elif (
            self.api_key
            and self.api_secret
            and self.access_token
            and self.access_token_secret
        ):
            self._init_client_v1()
        else:
            logger.warning(
                "Twitter credentials not found. Set TWITTER_BEARER_TOKEN or Twitter v1.1 credentials."
            )

    def _init_client_v2(self):
        """Initialize Twitter API v2 client."""
        try:
            self.client = tweepy.Client(bearer_token=self.bearer_token)
            logger.info("[OK] Twitter API v2 client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API v2: {e}")

    def _init_client_v1(self):
        """Initialize Twitter API v1.1 client."""
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            self.api = tweepy.API(auth)
            logger.info("[OK] Twitter API v1.1 client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API v1.1: {e}")

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user data by username."""
        try:
            if self.client:
                # API v2
                user = self.client.get_user(username=username, user_fields=["public_metrics"])
                return {
                    "id": user.data.id,
                    "username": user.data.username,
                    "name": user.data.name,
                    "followers_count": user.data.public_metrics.get("followers_count", 0),
                    "tweets_count": user.data.public_metrics.get("tweet_count", 0),
                    "following_count": user.data.public_metrics.get("following_count", 0),
                }
            elif self.api:
                # API v1.1
                user = self.api.get_user(screen_name=username)
                return {
                    "id": user.id,
                    "username": user.screen_name,
                    "name": user.name,
                    "followers_count": user.followers_count,
                    "tweets_count": user.statuses_count,
                    "following_count": user.friends_count,
                }
        except Exception as e:
            logger.error(f"Error fetching user {username}: {e}")
        return None

    def get_user_tweets(
        self, username: str, max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent tweets from a user."""
        try:
            if not self.client:
                logger.warning("Twitter API v2 client not initialized")
                return []

            # Get user ID first
            user_data = self.get_user_by_username(username)
            if not user_data:
                return []

            user_id = user_data["id"]

            # Get tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=[
                    "public_metrics",
                    "created_at",
                    "author_id",
                    "conversation_id",
                ],
            )

            result = []
            if tweets.data:
                for tweet in tweets.data:
                    result.append(
                        {
                            "id": tweet.id,
                            "text": tweet.text,
                            "created_at": tweet.created_at,
                            "likes": tweet.public_metrics.get("like_count", 0),
                            "retweets": tweet.public_metrics.get("retweet_count", 0),
                            "replies": tweet.public_metrics.get("reply_count", 0),
                            "quotes": tweet.public_metrics.get("quote_count", 0),
                            "author_id": tweet.author_id,
                        }
                    )
            return result

        except Exception as e:
            logger.error(f"Error fetching tweets for {username}: {e}")
            return []

    def get_tweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Get a single tweet by ID."""
        try:
            if self.client:
                tweet = self.client.get_tweet(
                    id=tweet_id,
                    tweet_fields=[
                        "public_metrics",
                        "created_at",
                        "author_id",
                        "conversation_id",
                    ],
                )
                if tweet.data:
                    return {
                        "id": tweet.data.id,
                        "text": tweet.data.text,
                        "created_at": tweet.data.created_at,
                        "likes": tweet.data.public_metrics.get("like_count", 0),
                        "retweets": tweet.data.public_metrics.get("retweet_count", 0),
                        "replies": tweet.data.public_metrics.get("reply_count", 0),
                        "quotes": tweet.data.public_metrics.get("quote_count", 0),
                        "author_id": tweet.data.author_id,
                    }
        except Exception as e:
            logger.error(f"Error fetching tweet {tweet_id}: {e}")
        return None

    def get_tweet_liking_users(self, tweet_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get users who liked a tweet."""
        try:
            if not self.client:
                return []

            users = self.client.get_liking_users(
                id=tweet_id,
                max_results=min(max_results, 100),
                user_fields=["public_metrics", "created_at"],
            )

            result = []
            if users.data:
                for user in users.data:
                    result.append(
                        {
                            "id": user.id,
                            "username": user.username,
                            "name": user.name,
                            "followers_count": user.public_metrics.get("followers_count", 0),
                        }
                    )
            return result

        except Exception as e:
            logger.error(f"Error fetching liking users for tweet {tweet_id}: {e}")
            return []

    def search_tweets(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for tweets matching a query."""
        try:
            if not self.client:
                return []

            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=["public_metrics", "created_at", "author_id"],
            )

            result = []
            if tweets.data:
                for tweet in tweets.data:
                    result.append(
                        {
                            "id": tweet.id,
                            "text": tweet.text,
                            "created_at": tweet.created_at,
                            "likes": tweet.public_metrics.get("like_count", 0),
                            "retweets": tweet.public_metrics.get("retweet_count", 0),
                            "author_id": tweet.author_id,
                        }
                    )
            return result

        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []

    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from tweet text."""
        import re
        hashtags = re.findall(r"#\w+", text)
        return [tag.lower() for tag in hashtags]

    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from tweet text."""
        import re
        mentions = re.findall(r"@\w+", text)
        return [mention.lower() for mention in mentions]

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from tweet text."""
        import re
        urls = re.findall(r"https?://\S+", text)
        return urls

    def parse_tweet(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """Parse tweet data into standard format."""
        text = tweet.get("text", "")
        return {
            "id": tweet.get("id"),
            "text": text,
            "created_at": tweet.get("created_at"),
            "hashtags": self.extract_hashtags(text),
            "mentions": self.extract_mentions(text),
            "urls": self.extract_urls(text),
            "engagement": {
                "likes": tweet.get("likes", 0),
                "retweets": tweet.get("retweets", 0),
                "replies": tweet.get("replies", 0),
                "quotes": tweet.get("quotes", 0),
                "engagement_rate": self._calculate_engagement_rate(tweet),
            },
        }

    def _calculate_engagement_rate(self, tweet: Dict[str, Any]) -> float:
        """Calculate engagement rate for a tweet."""
        total_engagement = (
            tweet.get("likes", 0)
            + tweet.get("retweets", 0)
            + tweet.get("replies", 0)
            + tweet.get("quotes", 0)
        )
        # Assuming ~1000 impressions as baseline
        return min(1.0, total_engagement / 1000)


def get_twitter_client() -> TwitterClient:
    """Get Twitter client instance."""
    return TwitterClient()
