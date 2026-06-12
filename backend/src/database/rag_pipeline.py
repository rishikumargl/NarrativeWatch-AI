"""RAG pipeline for ingestion and retrieval using PostgreSQL + pgvector."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.database.models import InstagramPost, InstagramPage, BiasPattern
from src.database.postgres_client import get_client
from src.utils.embedding_utils import get_embedding_client
from src.apis.instagram_api import InstagramAPI

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for data ingestion and similarity-based retrieval."""

    def __init__(self):
        """Initialize RAG pipeline."""
        self.db_client = get_client()
        self.embedding_client = get_embedding_client()
        self.instagram_api = InstagramAPI()
        logger.info("[OK] RAG pipeline initialized")

    # ==================== INGESTION ====================

    def ingest_instagram_post(
        self,
        post_id: str,
        page_username: str,
        caption: str,
        hashtags: Optional[List[str]] = None,
        content_type: str = "text",
        likes: int = 0,
        comments: int = 0,
        posting_time: Optional[datetime] = None,
    ) -> str:
        """Ingest Instagram post into vector database.

        Args:
            post_id: Unique post ID
            page_username: Username of posting page
            caption: Post caption
            hashtags: List of hashtags
            content_type: Type of content (image, video, etc.)
            likes: Like count
            comments: Comment count
            posting_time: Time post was published

        Returns:
            Post ID if successful
        """
        try:
            # Generate embedding
            embedding = self.embedding_client.embed_instagram_post(
                caption=caption,
                hashtags=hashtags,
                content_type=content_type,
            )

            # Create post object
            post = InstagramPost(
                post_id=post_id,
                page_username=page_username,
                caption=caption,
                hashtags=hashtags or [],
                content_type=content_type,
                embedding=embedding,
                likes=likes,
                comments=comments,
                posting_time=posting_time or datetime.utcnow(),
                trust_score=None,  # Will be filled by analysis agents
            )

            # Save to database
            session = self.db_client.get_session()
            try:
                session.add(post)
                session.commit()
                logger.info(f"[OK] Ingested post: {post_id}")
                return post_id
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error ingesting post {post_id}: {e}")
            raise

    def ingest_instagram_page(
        self,
        page_id: str,
        username: str,
        display_name: Optional[str] = None,
        biography: Optional[str] = None,
        followers: int = 0,
        following: int = 0,
        post_count: int = 0,
    ) -> str:
        """Ingest Instagram page into vector database.

        Args:
            page_id: Unique page ID
            username: Page username
            display_name: Display name
            biography: Page biography
            followers: Follower count
            following: Following count
            post_count: Number of posts

        Returns:
            Page ID if successful
        """
        try:
            # Generate embedding
            embedding = self.embedding_client.embed_instagram_page(
                username=username,
                biography=biography,
            )

            # Create page object
            page = InstagramPage(
                page_id=page_id,
                username=username,
                display_name=display_name,
                biography=biography,
                embedding=embedding,
                followers=followers,
                following=following,
                post_count=post_count,
            )

            # Save to database
            session = self.db_client.get_session()
            try:
                session.add(page)
                session.commit()
                logger.info(f"[OK] Ingested page: {username}")
                return page_id
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error ingesting page {username}: {e}")
            raise

    def ingest_bias_pattern(
        self,
        pattern_id: str,
        bias_category: str,
        pattern_description: str,
        indicators: List[str],
        frequency_score: float = 0.5,
        severity_score: float = 0.5,
    ) -> str:
        """Ingest bias pattern into vector database.

        Args:
            pattern_id: Unique pattern ID
            bias_category: Type of bias
            pattern_description: Description of pattern
            indicators: List of indicators
            frequency_score: How common (0-1)
            severity_score: Severity (0-1)

        Returns:
            Pattern ID if successful
        """
        try:
            # Generate embedding
            embedding = self.embedding_client.embed_text(pattern_description)

            # Create pattern object
            pattern = BiasPattern(
                pattern_id=pattern_id,
                bias_category=bias_category,
                pattern_description=pattern_description,
                indicators=indicators,
                frequency_score=frequency_score,
                severity_score=severity_score,
                pattern_embedding=embedding,
            )

            # Save to database
            session = self.db_client.get_session()
            try:
                session.add(pattern)
                session.commit()
                logger.info(f"[OK] Ingested bias pattern: {pattern_id}")
                return pattern_id
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error ingesting pattern {pattern_id}: {e}")
            raise

    # ==================== RETRIEVAL ====================

    def search_similar_posts(
        self,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search for similar posts using vector similarity.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum results
            similarity_threshold: Minimum similarity score

        Returns:
            List of similar posts with similarity scores
        """
        try:
            session = self.db_client.get_session()
            try:
                # Use pgvector similarity search
                results = (
                    session.query(
                        InstagramPost,
                        InstagramPost.embedding.cosine_distance(query_embedding).label(
                            "distance"
                        ),
                    )
                    .order_by("distance")
                    .limit(limit)
                    .all()
                )

                # Convert distance to similarity (1 - distance)
                similar_posts = []
                for post, distance in results:
                    similarity = 1 - distance
                    if similarity >= similarity_threshold:
                        similar_posts.append(
                            {
                                "post_id": post.post_id,
                                "caption": post.caption,
                                "page_username": post.page_username,
                                "similarity": float(similarity),
                                "trust_score": post.trust_score,
                                "hashtags": post.hashtags,
                            }
                        )

                logger.info(f"Found {len(similar_posts)} similar posts")
                return similar_posts
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error searching similar posts: {e}")
            return []

    def search_similar_pages(
        self,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search for similar pages using vector similarity.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum results
            similarity_threshold: Minimum similarity score

        Returns:
            List of similar pages with similarity scores
        """
        try:
            session = self.db_client.get_session()
            try:
                # Use pgvector similarity search
                results = (
                    session.query(
                        InstagramPage,
                        InstagramPage.embedding.cosine_distance(query_embedding).label(
                            "distance"
                        ),
                    )
                    .order_by("distance")
                    .limit(limit)
                    .all()
                )

                # Convert distance to similarity
                similar_pages = []
                for page, distance in results:
                    similarity = 1 - distance
                    if similarity >= similarity_threshold:
                        similar_pages.append(
                            {
                                "page_id": page.page_id,
                                "username": page.username,
                                "followers": page.followers,
                                "similarity": float(similarity),
                                "average_trust_score": page.average_trust_score,
                            }
                        )

                logger.info(f"Found {len(similar_pages)} similar pages")
                return similar_pages
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error searching similar pages: {e}")
            return []

    def search_bias_patterns(
        self,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search for similar bias patterns.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum results
            similarity_threshold: Minimum similarity score

        Returns:
            List of similar bias patterns
        """
        try:
            session = self.db_client.get_session()
            try:
                # Use pgvector similarity search
                results = (
                    session.query(
                        BiasPattern,
                        BiasPattern.pattern_embedding.cosine_distance(
                            query_embedding
                        ).label("distance"),
                    )
                    .order_by("distance")
                    .limit(limit)
                    .all()
                )

                # Convert distance to similarity
                similar_patterns = []
                for pattern, distance in results:
                    similarity = 1 - distance
                    if similarity >= similarity_threshold:
                        similar_patterns.append(
                            {
                                "pattern_id": pattern.pattern_id,
                                "bias_category": pattern.bias_category,
                                "indicators": pattern.indicators,
                                "similarity": float(similarity),
                                "severity_score": pattern.severity_score,
                            }
                        )

                logger.info(f"Found {len(similar_patterns)} similar bias patterns")
                return similar_patterns
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error searching bias patterns: {e}")
            return []

    # ==================== UTILITIES ====================

    def get_post_count(self) -> int:
        """Get total number of posts in RAG database."""
        try:
            session = self.db_client.get_session()
            try:
                count = session.query(func.count(InstagramPost.post_id)).scalar()
                return count or 0
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error getting post count: {e}")
            return 0

    def get_page_count(self) -> int:
        """Get total number of pages in RAG database."""
        try:
            session = self.db_client.get_session()
            try:
                count = session.query(func.count(InstagramPage.page_id)).scalar()
                return count or 0
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0

    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics."""
        return {
            "posts": self.get_post_count(),
            "pages": self.get_page_count(),
            "embedding_cache_size": self.embedding_client.cache_stats()["size"],
        }


# Global RAG pipeline instance
_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create global RAG pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
