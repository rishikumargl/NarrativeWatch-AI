"""Utility modules for NarrativeWatch AI."""

from .embedding_utils import (
    EmbeddingClient,
    EmbeddingCache,
    get_embedding_client,
    embed_text,
    embed_batch,
    similarity,
)

__all__ = [
    "EmbeddingClient",
    "EmbeddingCache",
    "get_embedding_client",
    "embed_text",
    "embed_batch",
    "similarity",
]
