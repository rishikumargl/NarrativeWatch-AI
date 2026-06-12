"""Tests for embedding utilities."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.embedding_utils import (
    EmbeddingClient,
    EmbeddingCache,
    embed_text,
    embed_batch,
    similarity,
)


class TestEmbeddingCache:
    """Test embedding cache."""

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = EmbeddingCache(ttl_hours=24)
        assert cache.size() == 0

    def test_cache_set_and_get(self):
        """Test setting and retrieving from cache."""
        cache = EmbeddingCache()
        text = "test text"
        embedding = [0.1] * 1536

        cache.set(text, embedding)
        retrieved = cache.get(text)

        assert retrieved == embedding

    def test_cache_miss(self):
        """Test cache miss."""
        cache = EmbeddingCache()
        result = cache.get("nonexistent")
        assert result is None

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = EmbeddingCache()
        cache.set("text1", [0.1] * 1536)
        cache.set("text2", [0.2] * 1536)

        assert cache.size() == 2
        cache.clear()
        assert cache.size() == 0


class TestEmbeddingClient:
    """Test embedding client."""

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_initialization(self, mock_model, mock_init):
        """Test client initialization."""
        client = EmbeddingClient()
        assert client.project_id == "test_project"
        assert client.model_name == "text-embedding-005"
        assert client.use_cache == True

    def test_missing_project_id(self):
        """Test error when project ID is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="VERTEX_AI_PROJECT_ID"):
                EmbeddingClient()

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_embed_text(self, mock_model_class, mock_init):
        """Test text embedding."""
        # Mock embedding model
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1] * 1536

        mock_model = MagicMock()
        mock_model.get_embeddings.return_value = [mock_embedding]
        mock_model_class.return_value = mock_model

        client = EmbeddingClient()
        embedding = client.embed_text("test text")

        assert len(embedding) == 1536
        assert embedding[0] == 0.1

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_embed_text_caching(self, mock_model_class, mock_init):
        """Test that embeddings are cached."""
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1] * 1536

        mock_model = MagicMock()
        mock_model.get_embeddings.return_value = [mock_embedding]
        mock_model_class.return_value = mock_model

        client = EmbeddingClient(use_cache=True)

        # First call should hit API
        text = "test text"
        embedding1 = client.embed_text(text)

        # Second call should hit cache (API not called)
        embedding2 = client.embed_text(text)

        assert embedding1 == embedding2
        assert mock_model.get_embeddings.call_count == 1  # Only called once

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_embed_batch(self, mock_model_class, mock_init):
        """Test batch embedding."""
        mock_embeddings = [MagicMock(values=[0.1 * i] * 1536) for i in range(3)]

        mock_model = MagicMock()
        mock_model.get_embeddings.return_value = mock_embeddings
        mock_model_class.return_value = mock_model

        client = EmbeddingClient()
        texts = ["text1", "text2", "text3"]
        embeddings = client.embed_batch(texts, batch_size=100)

        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_embed_instagram_post(self, mock_model_class, mock_init):
        """Test Instagram post embedding."""
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1] * 1536

        mock_model = MagicMock()
        mock_model.get_embeddings.return_value = [mock_embedding]
        mock_model_class.return_value = mock_model

        client = EmbeddingClient(use_cache=False)
        embedding = client.embed_instagram_post(
            caption="Nice photo",
            hashtags=["#photography", "#nature"],
            content_type="image",
        )

        assert len(embedding) == 1536

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_similarity(self, mock_model_class, mock_init):
        """Test similarity calculation."""
        client = EmbeddingClient()

        # Test similar embeddings
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.9, 0.1, 0.0]

        sim = client.similarity(embedding1, embedding2)
        assert 0.95 < sim <= 1.0  # Should be very similar

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_similarity_orthogonal(self, mock_model_class, mock_init):
        """Test similarity for orthogonal vectors."""
        client = EmbeddingClient()

        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]

        sim = client.similarity(embedding1, embedding2)
        assert sim == 0.0  # Orthogonal vectors have 0 similarity

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_health_check(self, mock_model_class, mock_init):
        """Test health check."""
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1] * 1536

        mock_model = MagicMock()
        mock_model.get_embeddings.return_value = [mock_embedding]
        mock_model_class.return_value = mock_model

        client = EmbeddingClient(use_cache=False)
        is_healthy = client.check_health()

        assert is_healthy == True

    @patch.dict(os.environ, {"VERTEX_AI_PROJECT_ID": "test_project"})
    @patch("vertexai.init")
    @patch("vertexai.language_models.TextEmbeddingModel.from_pretrained")
    def test_cache_stats(self, mock_model_class, mock_init):
        """Test cache statistics."""
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1] * 1536

        mock_model = MagicMock()
        mock_model.get_embeddings.return_value = [mock_embedding]
        mock_model_class.return_value = mock_model

        client = EmbeddingClient(use_cache=True)
        client.embed_text("test")

        stats = client.cache_stats()
        assert stats["enabled"] == True
        assert stats["size"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
