"""RAG pipeline for ingestion and retrieval using PostgreSQL + pgvector."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.connection import SessionLocal
from src.utils.embedding_utils import get_embedding_client

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for data ingestion and similarity-based retrieval."""

    def __init__(self):
        """Initialize RAG pipeline."""
        self.embedding_client = get_embedding_client()
        self.db = SessionLocal()
        logger.info("[OK] RAG pipeline initialized")

    def ingest_article(
        self,
        title: str,
        content: str,
        source: str = "NewsAPI",
        url: Optional[str] = None,
        author: Optional[str] = None,
        published_at: Optional[datetime] = None,
    ) -> Optional[str]:
        """Ingest article into vector database.

        Args:
            title: Article title
            content: Article content
            source: Source of the article
            url: Article URL
            author: Article author
            published_at: Publication datetime

        Returns:
            Article ID if successful
        """
        try:
            embedding = self.embedding_client.embed_text(content)
            if not embedding:
                logger.warning("Failed to generate embedding for article")
                return None

            query = text("""
                INSERT INTO news_articles
                (title, content, source, url, author, published_at, content_embedding, created_at)
                VALUES
                (:title, :content, :source, :url, :author, :published_at, :embedding, :created_at)
                RETURNING id
            """)

            result = self.db.execute(query, {
                "title": title,
                "content": content,
                "source": source,
                "url": url or "",
                "author": author or "",
                "published_at": published_at or datetime.utcnow(),
                "embedding": embedding,
                "created_at": datetime.utcnow(),
            })

            article_id = result.scalar()
            self.db.commit()
            logger.info(f"Ingested article: {title[:50]}... (ID: {article_id})")
            return str(article_id)

        except Exception as e:
            logger.error(f"Failed to ingest article: {e}")
            self.db.rollback()
            return None

    def search_similar(
        self,
        query_text: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for similar articles using semantic similarity.

        Args:
            query_text: Query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar articles
        """
        try:
            # Generate embedding for query
            query_embedding = self.embedding_client.embed_text(query_text)
            if not query_embedding:
                logger.warning("Failed to generate embedding for query")
                return []

            # Search using pgvector cosine similarity
            sql = text("""
                SELECT
                    id,
                    title,
                    content,
                    source,
                    url,
                    author,
                    published_at,
                    (1 - (content_embedding <=> :embedding)) as similarity
                FROM news_articles
                WHERE (1 - (content_embedding <=> :embedding)) > :threshold
                ORDER BY similarity DESC
                LIMIT :limit
            """)

            results = self.db.execute(sql, {
                "embedding": query_embedding,
                "threshold": similarity_threshold,
                "limit": top_k
            })

            articles = []
            for row in results:
                articles.append({
                    "id": row.id,
                    "title": row.title,
                    "content": row.content[:500],  # First 500 chars
                    "source": row.source,
                    "url": row.url,
                    "author": row.author,
                    "published_at": row.published_at.isoformat() if row.published_at else None,
                    "similarity": float(row.similarity)
                })

            logger.info(f"Found {len(articles)} similar articles")
            return articles

        except Exception as e:
            logger.error(f"Failed to search similar articles: {e}")
            return []

    def get_context(
        self,
        query_text: str,
        num_results: int = 3
    ) -> str:
        """Get context for a query from similar articles.

        Args:
            query_text: Query text
            num_results: Number of articles to use for context

        Returns:
            Context string for LLM
        """
        similar = self.search_similar(query_text, top_k=num_results)

        if not similar:
            return "No relevant context found in database."

        context = "Relevant articles from database:\n\n"
        for i, article in enumerate(similar, 1):
            context += f"{i}. {article['title']}\n"
            context += f"   Source: {article['source']}\n"
            context += f"   Similarity: {article['similarity']:.2%}\n"
            context += f"   Content: {article['content'][:300]}...\n\n"

        return context

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
            logger.info("RAG pipeline closed")


# Global instance
_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
