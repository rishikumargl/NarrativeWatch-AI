"""API routes for document ingestion and RAG management."""

import logging
from typing import Optional, List
from pydantic import BaseModel
from src.services.document_ingestion_service import document_ingestion_service

logger = logging.getLogger(__name__)


# ==================== REQUEST MODELS ====================


class DocumentUploadRequest(BaseModel):
    """Request model for single document upload."""
    title: str
    content: str
    source_url: str
    source_domain: str
    author: Optional[str] = None
    publish_date: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class BatchDocumentUploadRequest(BaseModel):
    """Request model for batch document upload."""
    documents: List[DocumentUploadRequest]


class DocumentStatsResponse(BaseModel):
    """Response model for document statistics."""
    total_documents: int
    unique_sources: int
    unique_categories: int
    with_embeddings: int
    oldest_document: Optional[str]
    newest_document: Optional[str]


# ==================== HANDLERS ====================


async def upload_document(request: DocumentUploadRequest) -> dict:
    """
    Upload a single news document for RAG ingestion.

    Returns:
        {
            "success": bool,
            "document_id": str,
            "message": str,
            "embedding_stored": bool
        }
    """
    try:
        logger.info(f"Uploading document: {request.title[:50]}")

        result = await document_ingestion_service.ingest_document(
            title=request.title,
            content=request.content,
            source_url=request.source_url,
            source_domain=request.source_domain,
            author=request.author,
            publish_date=request.publish_date,
            category=request.category,
            tags=request.tags
        )

        return result
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return {
            "success": False,
            "document_id": None,
            "message": f"Error uploading document: {str(e)}",
            "embedding_stored": False,
            "chunks_created": 0
        }


async def upload_batch_documents(request: BatchDocumentUploadRequest) -> dict:
    """
    Upload multiple news documents for RAG ingestion.

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
    try:
        logger.info(f"Uploading batch of {len(request.documents)} documents")

        documents = [doc.dict() for doc in request.documents]
        result = await document_ingestion_service.ingest_batch(documents)

        return result
    except Exception as e:
        logger.error(f"Error uploading batch documents: {e}")
        return {
            "success": False,
            "total_documents": len(request.documents),
            "ingested_count": 0,
            "skipped_count": 0,
            "failed_count": len(request.documents),
            "document_ids": [],
            "errors": [str(e)]
        }


async def get_document_statistics() -> dict:
    """
    Get statistics about ingested documents in RAG system.

    Returns:
        {
            "total_documents": int,
            "unique_sources": int,
            "unique_categories": int,
            "with_embeddings": int,
            "oldest_document": str,
            "newest_document": str
        }
    """
    try:
        logger.info("Fetching document statistics")
        stats = document_ingestion_service.get_document_stats()  # Sync, not async
        return stats
    except Exception as e:
        logger.error(f"Error fetching document statistics: {e}")
        return {
            "total_documents": 0,
            "unique_sources": 0,
            "unique_categories": 0,
            "with_embeddings": 0,
            "oldest_document": None,
            "newest_document": None,
            "error": str(e)
        }
