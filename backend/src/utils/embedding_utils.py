"""Embedding utilities for NarrativeWatch AI using Vertex AI."""

from typing import List, Optional, Dict
import numpy as np
import logging

try:
    from src.config import get_config
except ImportError:
    from config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class EmbeddingUtils:
    """Utilities for generating and handling embeddings."""

    def __init__(self):
        """Initialize embedding utilities."""
        try:
            from langchain_google_vertexai.embeddings import VertexAIEmbeddings
            self.embeddings = VertexAIEmbeddings(
                model_name=config.EMBEDDING_MODEL,
                project=config.VERTEX_AI_PROJECT,
                location=config.VERTEX_AI_LOCATION
            )
            self.embedding_dim = config.VECTOR_DIMENSION
            logger.info(f"Initialized Vertex AI embeddings (dim={self.embedding_dim})")
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI embeddings: {e}")
            logger.info("Using mock embeddings for testing")
            self.embeddings = None
            self.embedding_dim = config.VECTOR_DIMENSION

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector or None if failed
        """
        if not text or not isinstance(text, str):
            logger.warning("Invalid input for embedding generation")
            return None

        try:
            if self.embeddings:
                embedding = self.embeddings.embed_query(text)
                return embedding
            else:
                # Mock embedding for testing
                return self._mock_embedding(text)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def batch_embedding(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            if self.embeddings:
                embeddings = self.embeddings.embed_documents(texts)
                return embeddings
            else:
                # Mock embeddings for testing
                return [self._mock_embedding(text) for text in texts]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [None] * len(texts)

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (0-1)
        """
        if not vec1 or not vec2:
            return 0.0

        try:
            arr1 = np.array(vec1, dtype=np.float32)
            arr2 = np.array(vec2, dtype=np.float32)

            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            # Ensure result is in [0, 1]
            return float(np.clip(similarity, 0, 1))
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0

    def euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate Euclidean distance between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Euclidean distance
        """
        if not vec1 or not vec2:
            return float('inf')

        try:
            arr1 = np.array(vec1, dtype=np.float32)
            arr2 = np.array(vec2, dtype=np.float32)
            distance = np.linalg.norm(arr1 - arr2)
            return float(distance)
        except Exception as e:
            logger.error(f"Failed to calculate euclidean distance: {e}")
            return float('inf')

    def find_similar_vectors(
        self,
        query_vector: List[float],
        vectors: List[List[float]],
        top_k: int = 5,
        metric: str = 'cosine'
    ) -> List[tuple]:
        """
        Find top-k similar vectors to query vector.

        Args:
            query_vector: Query vector
            vectors: List of vectors to search
            top_k: Number of top results to return
            metric: Similarity metric ('cosine' or 'euclidean')

        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        if not query_vector or not vectors:
            return []

        similarities = []
        for idx, vec in enumerate(vectors):
            if metric == 'cosine':
                sim = self.cosine_similarity(query_vector, vec)
            else:  # euclidean
                dist = self.euclidean_distance(query_vector, vec)
                sim = 1 / (1 + dist)  # Convert distance to similarity

            similarities.append((idx, sim))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def normalize_vector(self, vector: List[float]) -> List[float]:
        """
        Normalize vector to unit length.

        Args:
            vector: Input vector

        Returns:
            Normalized vector
        """
        if not vector:
            return []

        try:
            arr = np.array(vector, dtype=np.float32)
            norm = np.linalg.norm(arr)
            if norm == 0:
                return vector
            return (arr / norm).tolist()
        except Exception as e:
            logger.error(f"Failed to normalize vector: {e}")
            return vector

    def average_embeddings(self, embeddings: List[List[float]]) -> Optional[List[float]]:
        """
        Calculate average of multiple embeddings.

        Args:
            embeddings: List of embedding vectors

        Returns:
            Average embedding vector
        """
        if not embeddings or any(e is None for e in embeddings):
            return None

        try:
            arr = np.array(embeddings, dtype=np.float32)
            avg = np.mean(arr, axis=0)
            return avg.tolist()
        except Exception as e:
            logger.error(f"Failed to average embeddings: {e}")
            return None

    def _mock_embedding(self, text: str, dim: int = 1536) -> List[float]:
        """
        Generate deterministic mock embedding based on text hash (for testing).

        Args:
            text: Input text
            dim: Embedding dimension

        Returns:
            Mock embedding vector
        """
        import hashlib
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
        np.random.seed(hash_value % (2**32))
        return np.random.randn(dim).tolist()

    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate embedding vector.

        Args:
            embedding: Embedding to validate

        Returns:
            True if valid, False otherwise
        """
        if not embedding or not isinstance(embedding, list):
            return False

        if len(embedding) != self.embedding_dim:
            logger.warning(f"Embedding dimension mismatch: {len(embedding)} vs {self.embedding_dim}")
            return False

        try:
            # Check if all values are valid floats
            for val in embedding:
                if not isinstance(val, (int, float)) or np.isnan(val) or np.isinf(val):
                    return False
            return True
        except Exception:
            return False


    def embed_instagram_post(self, caption: str, hashtags: List[str] = None, content_type: str = "text") -> Optional[List[float]]:
        """
        Generate embedding for Instagram post.

        Args:
            caption: Post caption text
            hashtags: List of hashtags
            content_type: Type of content (text, image, video)

        Returns:
            Embedding vector
        """
        if not caption:
            return None

        # Combine caption and hashtags for richer embedding
        text = caption
        if hashtags:
            text += " " + " ".join(hashtags)

        return self.generate_embedding(text)

    def embed_instagram_page(self, username: str, biography: str = None) -> Optional[List[float]]:
        """
        Generate embedding for Instagram page.

        Args:
            username: Page username
            biography: Page biography/description

        Returns:
            Embedding vector
        """
        text = username
        if biography:
            text += " " + biography

        return self.generate_embedding(text)

    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for arbitrary text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        return self.generate_embedding(text)

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate similarity between two vectors. Alias for cosine_similarity.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        return self.cosine_similarity(vec1, vec2)

    def cache_stats(self) -> Dict[str, int]:
        """
        Get embedding cache statistics.

        Returns:
            Cache statistics dictionary
        """
        # Placeholder for cache implementation
        # Can be extended to track actual cache hits/misses
        return {
            "cache_size": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_hit_rate": 0.0
        }


# Singleton instance and factory function
_embedding_client = None


def get_embedding_client() -> EmbeddingUtils:
    """
    Get or create the embedding client singleton.

    Returns:
        EmbeddingUtils instance
    """
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = EmbeddingUtils()
    return _embedding_client
