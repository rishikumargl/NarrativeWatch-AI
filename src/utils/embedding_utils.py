"""Embedding generation utilities for vector storage."""

import os
import logging
from typing import List, Optional, Union
from functools import lru_cache
import numpy as np
from vertexai.language_models import TextEmbeddingModel
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Simple cache for embeddings to avoid redundant API calls."""

    def __init__(self, ttl_hours: int = 24):
        """Initialize embedding cache.

        Args:
            ttl_hours: Time-to-live for cached embeddings in hours
        """
        self.cache: dict = {}
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"✓ Embedding cache initialized (TTL: {ttl_hours}h)")

    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache if valid.

        Args:
            text: Text to look up

        Returns:
            Embedding or None if not cached or expired
        """
        if text not in self.cache:
            return None

        embedding, timestamp = self.cache[text]
        if datetime.utcnow() - timestamp > self.ttl:
            del self.cache[text]
            return None

        return embedding

    def set(self, text: str, embedding: List[float]):
        """Cache an embedding.

        Args:
            text: Original text
            embedding: Vector embedding
        """
        self.cache[text] = (embedding, datetime.utcnow())

    def clear(self):
        """Clear all cached embeddings."""
        self.cache.clear()
        logger.info("✓ Embedding cache cleared")

    def size(self) -> int:
        """Get number of cached embeddings."""
        return len(self.cache)


class EmbeddingClient:
    """Client for generating text embeddings using Vertex AI."""

    def __init__(
        self,
        model_name: str = "text-embedding-005",
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        use_cache: bool = True,
    ):
        """Initialize embedding client.

        Args:
            model_name: Vertex AI embedding model name
            project_id: Google Cloud project ID
            location: GCP region
            use_cache: Whether to cache embeddings
        """
        self.model_name = model_name
        self.project_id = project_id or os.getenv("VERTEX_AI_PROJECT_ID")
        self.location = location or os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.use_cache = use_cache

        if not self.project_id:
            raise ValueError("VERTEX_AI_PROJECT_ID environment variable not set")

        # Initialize model
        try:
            import vertexai
            vertexai.init(project=self.project_id, location=self.location)
            self.model = TextEmbeddingModel.from_pretrained(model_name)
            logger.info(f"✓ Embedding model initialized: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise

        # Initialize cache
        self.cache = EmbeddingCache() if use_cache else None

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536 dimensions)
        """
        # Check cache
        if self.cache:
            cached = self.cache.get(text)
            if cached:
                logger.debug(f"✓ Retrieved cached embedding for text ({len(text)} chars)")
                return cached

        # Generate embedding
        try:
            logger.info(f"Embedding text ({len(text)} chars)...")
            embeddings = self.model.get_embeddings([text])
            embedding = embeddings[0].values

            # Cache result
            if self.cache:
                self.cache.set(text, embedding)

            logger.info(f"✓ Generated embedding ({len(embedding)} dims)")
            return embedding

        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed
            batch_size: Max texts per batch (max 100)

        Returns:
            List of embedding vectors
        """
        batch_size = min(batch_size, 100)  # API limit
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            logger.info(f"Embedding batch {i // batch_size + 1} ({len(batch)} texts)...")

            # Check cache for this batch
            batch_embeddings = []
            uncached_indices = []
            uncached_texts = []

            for idx, text in enumerate(batch):
                if self.cache:
                    cached = self.cache.get(text)
                    if cached:
                        batch_embeddings.append(cached)
                        continue

                uncached_indices.append(idx)
                uncached_texts.append(text)

            # Generate embeddings for uncached texts
            if uncached_texts:
                try:
                    generated = self.model.get_embeddings(uncached_texts)
                    generated_embeddings = [e.values for e in generated]

                    # Insert back in correct positions and cache
                    for orig_idx, gen_idx in enumerate(uncached_indices):
                        embedding = generated_embeddings[orig_idx]
                        batch_embeddings.insert(gen_idx, embedding)

                        if self.cache:
                            self.cache.set(uncached_texts[orig_idx], embedding)

                except Exception as e:
                    logger.error(f"Batch embedding error: {e}")
                    raise

            embeddings.extend(batch_embeddings)
            logger.info(f"✓ Batch complete ({len(batch)} embeddings)")

        return embeddings

    def embed_instagram_post(
        self,
        caption: str,
        hashtags: Optional[List[str]] = None,
        content_type: Optional[str] = None,
    ) -> List[float]:
        """Generate embedding for Instagram post.

        Combines caption, hashtags, and content type for rich context.

        Args:
            caption: Post caption
            hashtags: List of hashtags
            content_type: Type of content (image, video, etc.)

        Returns:
            Embedding vector
        """
        # Build rich text representation
        parts = [caption] if caption else []

        if hashtags:
            parts.append(" ".join(hashtags))

        if content_type:
            parts.append(f"[{content_type}]")

        combined_text = " ".join(parts)
        return self.embed_text(combined_text)

    def embed_instagram_page(
        self,
        username: str,
        biography: Optional[str] = None,
        content_focus: Optional[List[str]] = None,
    ) -> List[float]:
        """Generate embedding for Instagram page.

        Combines username, bio, and content focus.

        Args:
            username: Page username
            biography: Page biography
            content_focus: List of content topics

        Returns:
            Embedding vector
        """
        parts = [username]

        if biography:
            parts.append(biography)

        if content_focus:
            parts.append(" ".join(content_focus))

        combined_text = " ".join(parts)
        return self.embed_text(combined_text)

    def embed_campaign(
        self,
        narrative_theme: str,
        hashtags: Optional[List[str]] = None,
    ) -> List[float]:
        """Generate embedding for campaign.

        Args:
            narrative_theme: Campaign narrative
            hashtags: Campaign hashtags

        Returns:
            Embedding vector
        """
        parts = [narrative_theme]

        if hashtags:
            parts.append(" ".join(hashtags))

        combined_text = " ".join(parts)
        return self.embed_text(combined_text)

    def similarity(
        self,
        embedding1: List[float],
        embedding2: List[float],
    ) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0-1)
        """
        arr1 = np.array(embedding1)
        arr2 = np.array(embedding2)

        # Cosine similarity
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

    def check_health(self) -> bool:
        """Check if embedding service is working.

        Returns:
            True if service is accessible
        """
        try:
            embedding = self.embed_text("test")
            is_healthy = embedding and len(embedding) == 1536
            logger.info(f"{'✓' if is_healthy else '✗'} Embedding service health: {is_healthy}")
            return is_healthy
        except Exception as e:
            logger.error(f"Embedding service health check failed: {e}")
            return False

    def cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Cache stats (size, enabled)
        """
        if not self.cache:
            return {"enabled": False, "size": 0}

        return {
            "enabled": True,
            "size": self.cache.size(),
        }


# Global embedding client instance
_client: Optional[EmbeddingClient] = None


def get_embedding_client() -> EmbeddingClient:
    """Get or create global embedding client."""
    global _client
    if _client is None:
        _client = EmbeddingClient()
    return _client


def embed_text(text: str) -> List[float]:
    """Convenience function to embed text using global client."""
    return get_embedding_client().embed_text(text)


def embed_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """Convenience function to batch embed texts using global client."""
    return get_embedding_client().embed_batch(texts, batch_size)


def similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Convenience function to calculate similarity using global client."""
    return get_embedding_client().similarity(embedding1, embedding2)
