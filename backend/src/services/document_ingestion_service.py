"""Document ingestion service for RAG pipeline with semantic chunking."""

import logging
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import text

from src.database.connection import SessionLocal

try:
    from src.utils.embedding_utils import get_embedding_client
except ImportError:
    get_embedding_client = None

logger = logging.getLogger(__name__)


def semantic_chunk_by_paragraphs(text: str, min_length: int = 100) -> List[str]:
    """
    Split document into semantic chunks by paragraph breaks.

    Preserves natural text boundaries (paragraphs) while maintaining
    semantic coherence. Ideal for news articles and documents with
    natural paragraph structure.

    Args:
        text: Document text to chunk
        min_length: Minimum chunk length (chars) - skip very small paragraphs

    Returns:
        List of paragraph chunks
    """
    if not text:
        return []

    # Split by double newlines (paragraph breaks)
    paragraphs = text.split('\n\n')

    # Filter empty and very short paragraphs
    chunks = [p.strip() for p in paragraphs if p.strip() and len(p.strip()) >= min_length]

    if not chunks:
        return [text.strip()] if text.strip() else []

    return chunks


class DocumentIngestionService:
    """Ingest and store documents in PostgreSQL for RAG retrieval."""

    def __init__(self):
        """Initialize document ingestion service."""
        self.db = SessionLocal()
        self.embedding_client = None
        if get_embedding_client:
            try:
                self.embedding_client = get_embedding_client()
            except Exception as e:
                logger.warning(f"Embedding client unavailable for ingestion: {e}")
        logger.info("[OK] Document ingestion service initialized")

    async def ingest_document(
        self,
        title: str,
        content: str,
        source_url: str,
        source_domain: str,
        author: Optional[str] = None,
        publish_date: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        use_semantic_chunks: bool = True
    ) -> Dict:
        """
        Ingest a news document into the RAG system with optional semantic chunking.

        Args:
            title: Document title
            content: Document content/body text
            source_url: Source URL
            source_domain: Domain of source
            author: Optional author name
            publish_date: Optional publish date
            category: Optional category (politics, sports, war, etc.)
            tags: Optional list of tags
            use_semantic_chunks: If True, chunk by paragraphs for better RAG retrieval

        Returns:
            {
                "success": bool,
                "document_id": str,
                "message": str,
                "embedding_stored": bool,
                "chunks_created": int
            }
        """
        try:
            logger.info(f"Ingesting document: {title[:50]}... from {source_domain}")

            # Generate document hash for deduplication
            doc_hash = hashlib.md5(f"{source_url}{content}".encode()).hexdigest()

            # Check if document already exists
            existing = self.db.execute(
                text("""
                    SELECT id FROM documents
                    WHERE document_hash = :hash
                """),
                {"hash": doc_hash}
            ).fetchone()

            if existing:
                logger.info(f"Document already ingested: {doc_hash}")
                return {
                    "success": True,
                    "document_id": str(existing[0]),
                    "message": "Document already ingested (duplicate)",
                    "embedding_stored": True,
                    "chunks_created": 0
                }

            # Apply semantic chunking if enabled
            chunks = []
            if use_semantic_chunks:
                chunks = semantic_chunk_by_paragraphs(content)
                logger.info(f"Created {len(chunks)} semantic chunks from document")

            # For full document embedding, use original content
            # For chunk-based RAG, we'll embed each chunk separately
            embedding = None
            embedding_stored = False
            chunks_created = 0

            # Try to embed full document (graceful fallback if unavailable)
            try:
                if self.embedding_client and hasattr(self.embedding_client, 'embed_text'):
                    embedding = self.embedding_client.embed_text(content)
                    embedding_stored = embedding is not None
                else:
                    embedding_stored = False
            except Exception as e:
                logger.warning(f"Failed to embed full document: {e}")
                embedding_stored = False

            # If using chunks, store them separately for finer-grained retrieval
            if use_semantic_chunks and chunks:
                try:
                    chunks_created = self._store_document_chunks(
                        parent_title=title,
                        chunks=chunks,
                        source_url=source_url,
                        source_domain=source_domain,
                        category=category
                    )
                    logger.info(f"Stored {chunks_created} document chunks for semantic RAG")
                except Exception as e:
                    logger.warning(f"Failed to store chunks: {e}")
                    chunks_created = 0

            # Insert full document into database
            query = text("""
                INSERT INTO documents (
                    title,
                    content,
                    source_url,
                    source_domain,
                    author,
                    publish_date,
                    category,
                    tags,
                    document_hash,
                    content_embedding,
                    ingestion_timestamp
                ) VALUES (
                    :title,
                    :content,
                    :source_url,
                    :source_domain,
                    :author,
                    :publish_date,
                    :category,
                    :tags,
                    :document_hash,
                    :embedding,
                    :timestamp
                )
                RETURNING id
            """)

            result = self.db.execute(query, {
                "title": title,
                "content": content,
                "source_url": source_url,
                "source_domain": source_domain,
                "author": author,
                "publish_date": publish_date,
                "category": category,
                "tags": tags,
                "document_hash": doc_hash,
                "embedding": embedding,
                "timestamp": datetime.utcnow()
            }).fetchone()

            self.db.commit()
            document_id = result[0]

            logger.info(f"Document ingested successfully: {document_id} ({chunks_created} chunks)")

            return {
                "success": True,
                "document_id": str(document_id),
                "message": f"Document ingested successfully with {chunks_created} semantic chunks",
                "embedding_stored": embedding_stored,
                "chunks_created": chunks_created
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error ingesting document: {str(e)}")
            return {
                "success": False,
                "document_id": None,
                "message": f"Failed to ingest document: {str(e)}",
                "embedding_stored": False,
                "chunks_created": 0
            }

    def _store_document_chunks(
        self,
        parent_title: str,
        chunks: List[str],
        source_url: str,
        source_domain: str,
        category: Optional[str] = None
    ) -> int:
        """
        Store semantic chunks for finer-grained RAG retrieval.

        Args:
            parent_title: Title of parent document
            chunks: List of text chunks
            source_url: Source URL
            source_domain: Source domain
            category: Optional category

        Returns:
            Number of chunks successfully stored
        """
        chunks_stored = 0

        for idx, chunk in enumerate(chunks):
            try:
                chunk_embedding = None
                if self.embedding_client:
                    try:
                        chunk_embedding = self.embedding_client.embed_text(chunk)
                    except Exception as e:
                        logger.warning(f"Failed to embed chunk {idx}: {e}")

                # Store chunk as separate document record
                query = text("""
                    INSERT INTO documents (
                        title,
                        content,
                        source_url,
                        source_domain,
                        category,
                        document_hash,
                        content_embedding,
                        ingestion_timestamp
                    ) VALUES (
                        :title,
                        :content,
                        :source_url,
                        :source_domain,
                        :category,
                        :document_hash,
                        :embedding,
                        :timestamp
                    )
                """)

                chunk_hash = hashlib.md5(f"{source_url}#{idx}#{chunk}".encode()).hexdigest()

                self.db.execute(query, {
                    "title": f"{parent_title} [Chunk {idx + 1}]",
                    "content": chunk,
                    "source_url": source_url,
                    "source_domain": source_domain,
                    "category": category,
                    "document_hash": chunk_hash,
                    "embedding": chunk_embedding,
                    "timestamp": datetime.utcnow()
                })

                chunks_stored += 1

            except Exception as e:
                logger.warning(f"Failed to store chunk {idx}: {e}")
                continue

        if chunks_stored > 0:
            try:
                self.db.commit()
            except Exception as e:
                logger.error(f"Failed to commit chunks: {e}")
                self.db.rollback()
                return 0

        return chunks_stored

    async def ingest_batch(
        self,
        documents: List[Dict]
    ) -> Dict:
        """
        Ingest multiple documents in batch.

        Args:
            documents: List of document dicts with keys:
                - title, content, source_url, source_domain
                - [optional] author, publish_date, category, tags

        Returns:
            {
                "success": bool,
                "total_documents": int,
                "ingested_count": int,
                "skipped_count": int,
                "failed_count": int,
                "document_ids": [str],
                "errors": [str]
            }
        """
        logger.info(f"Starting batch ingestion of {len(documents)} documents")

        ingested_count = 0
        skipped_count = 0
        failed_count = 0
        document_ids = []
        errors = []

        for idx, doc in enumerate(documents):
            try:
                result = await self.ingest_document(
                    title=doc.get("title", f"Document {idx}"),
                    content=doc.get("content", ""),
                    source_url=doc.get("source_url", ""),
                    source_domain=doc.get("source_domain", "unknown"),
                    author=doc.get("author"),
                    publish_date=doc.get("publish_date"),
                    category=doc.get("category"),
                    tags=doc.get("tags"),
                    use_semantic_chunks=doc.get("use_semantic_chunks", True)
                )

                if result["success"]:
                    if "already ingested" in result["message"]:
                        skipped_count += 1
                    else:
                        ingested_count += 1
                    document_ids.append(result["document_id"])
                else:
                    failed_count += 1
                    errors.append(f"Doc {idx}: {result['message']}")

            except Exception as e:
                failed_count += 1
                errors.append(f"Doc {idx}: {str(e)}")
                logger.error(f"Error ingesting document {idx}: {str(e)}")

        logger.info(f"Batch ingestion complete: {ingested_count} new, {skipped_count} skipped, {failed_count} failed")

        return {
            "success": failed_count == 0,
            "total_documents": len(documents),
            "ingested_count": ingested_count,
            "skipped_count": skipped_count,
            "failed_count": failed_count,
            "document_ids": document_ids,
            "errors": errors if errors else None
        }

    async def get_document_stats(self) -> Dict:
        """Get statistics about ingested documents."""
        try:
            stats = self.db.execute(text("""
                SELECT
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT source_domain) as unique_sources,
                    COUNT(DISTINCT category) as unique_categories,
                    COUNT(CASE WHEN content_embedding IS NOT NULL THEN 1 END) as with_embeddings,
                    MIN(ingestion_timestamp) as oldest_document,
                    MAX(ingestion_timestamp) as newest_document
                FROM documents
            """)).fetchone()

            return {
                "total_documents": stats[0] or 0,
                "unique_sources": stats[1] or 0,
                "unique_categories": stats[2] or 0,
                "with_embeddings": stats[3] or 0,
                "oldest_document": stats[4],
                "newest_document": stats[5]
            }

        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {
                "total_documents": 0,
                "unique_sources": 0,
                "unique_categories": 0,
                "with_embeddings": 0,
                "error": str(e)
            }

    def close(self):
        """Close database session."""
        if self.db:
            self.db.close()
            logger.info("Document ingestion service closed")


# Global service instance
document_ingestion_service = DocumentIngestionService()
