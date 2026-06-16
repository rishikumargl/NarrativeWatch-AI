"""RAG context retrieval service for historical data augmentation."""

import logging
from typing import Dict, List, Optional
from sqlalchemy import text
from datetime import datetime, timedelta

from src.database.connection import SessionLocal

try:
    from src.utils.embedding_utils import get_embedding_client
except ImportError:
    get_embedding_client = None

logger = logging.getLogger(__name__)


class RAGContextService:
    """Retrieve historical context from PostgreSQL + pgvector."""

    def __init__(self):
        """Initialize RAG service with database session."""
        self.db = SessionLocal()
        self.embedding_client = None
        if get_embedding_client:
            try:
                self.embedding_client = get_embedding_client()
            except Exception as e:
                logger.warning(f"Embedding client initialization failed (non-blocking): {e}")
        logger.info("[OK] RAG context service initialized")

    async def get_enriched_context(
        self,
        entities: List[Dict],
        source_domain: str,
        article_content: str
    ) -> Dict:
        """
        Retrieve historical context for entities and source.

        Args:
            entities: List of extracted entities with scores
            source_domain: Domain of article source
            article_content: Article content for similarity search

        Returns:
            {
                "entity_reputation": {
                    "entity_name": {
                        "mention_count": int,
                        "avg_trust_in_context": float,
                        "avg_bias_when_mentioned": float,
                        "recent_contexts": [str]
                    }
                },
                "source_baseline": {
                    "domain": str,
                    "article_count": int,
                    "avg_trust_score": float,
                    "avg_bias_score": float,
                    "risk_level": str
                },
                "similar_articles": [
                    {
                        "title": str,
                        "url": str,
                        "published_at": str,
                        "trust_score": float,
                        "similarity": float
                    }
                ],
                "total_context_items": int
            }
        """
        try:
            logger.info("🔍 Retrieving RAG context...")

            entity_reputation = await self._get_entity_reputation(entities)
            source_baseline = await self._get_source_baseline(source_domain)
            similar_articles = await self._search_similar_articles(article_content)

            total_items = len(entity_reputation) + 1 + len(similar_articles)
            logger.info(f"✅ RAG context retrieved: {len(entity_reputation)} entities + 1 source + {len(similar_articles)} similar articles")

            return {
                "entity_reputation": entity_reputation,
                "source_baseline": source_baseline,
                "similar_articles": similar_articles,
                "total_context_items": total_items
            }

        except Exception as e:
            logger.error(f"❌ Error retrieving RAG context: {str(e)}")
            return {
                "entity_reputation": {},
                "source_baseline": {
                    "domain": source_domain,
                    "article_count": 0,
                    "avg_trust_score": 50,
                    "avg_bias_score": 50,
                    "risk_level": "UNKNOWN"
                },
                "similar_articles": [],
                "total_context_items": 0
            }

    async def _get_entity_reputation(self, entities: List[Dict]) -> Dict:
        """Get historical reputation for extracted entities."""
        try:
            entity_reputation = {}

            # Get top entities by importance score
            top_entities = sorted(entities, key=lambda x: x.get("importance_score", 0), reverse=True)[:10]

            for entity in top_entities:
                entity_name = entity.get("name", "")
                entity_type = entity.get("type", "")

                # Query for mentions in past analyses
                query = text("""
                    SELECT
                        COUNT(*) as mention_count,
                        AVG(naa.trust_score) as avg_trust,
                        AVG(naa.overall_bias_score) as avg_bias
                    FROM news_article_analyses naa
                    WHERE naa.entities::text ILIKE :entity_pattern
                    AND naa.analysis_timestamp > :time_threshold
                """)

                result = self.db.execute(query, {
                    "entity_pattern": f"%{entity_name}%",
                    "time_threshold": datetime.utcnow() - timedelta(days=90)
                }).fetchone()

                if result and result[0] > 0:
                    entity_reputation[entity_name] = {
                        "type": entity_type,
                        "mention_count": int(result[0]),
                        "avg_trust_in_context": float(result[1]) if result[1] else 50.0,
                        "avg_bias_when_mentioned": float(result[2]) if result[2] else 50.0,
                        "recent_contexts": await self._get_entity_contexts(entity_name, 3)
                    }
                    logger.info(f"📊 Entity '{entity_name}' found in {result[0]} past analyses")

            return entity_reputation

        except Exception as e:
            logger.error(f"Error retrieving entity reputation: {e}")
            return {}

    async def _get_entity_contexts(self, entity_name: str, limit: int = 3) -> List[str]:
        """Get recent contexts where entity was mentioned."""
        try:
            query = text("""
                SELECT naa.full_report_summary
                FROM news_article_analyses naa
                WHERE naa.entities::text ILIKE :entity_pattern
                AND naa.full_report_summary IS NOT NULL
                ORDER BY naa.analysis_timestamp DESC
                LIMIT :limit
            """)

            results = self.db.execute(query, {
                "entity_pattern": f"%{entity_name}%",
                "limit": limit
            }).fetchall()

            return [str(row[0])[:200] for row in results if row[0]]

        except Exception as e:
            logger.debug(f"Error retrieving entity contexts: {e}")
            return []

    async def _get_source_baseline(self, source_domain: str) -> Dict:
        """Get baseline trust and bias scores for a news source."""
        try:
            query = text("""
                SELECT
                    COUNT(*) as article_count,
                    AVG(naa.trust_score) as avg_trust,
                    AVG(naa.overall_bias_score) as avg_bias,
                    COUNT(CASE WHEN naa.risk_level = 'HIGH' OR naa.risk_level = 'CRITICAL' THEN 1 END) as risky_count
                FROM news_article_analyses naa
                WHERE naa.article_url ILIKE :domain_pattern
                AND naa.analysis_timestamp > :time_threshold
            """)

            result = self.db.execute(query, {
                "domain_pattern": f"%{source_domain}%",
                "time_threshold": datetime.utcnow() - timedelta(days=180)
            }).fetchone()

            if result and result[0] > 0:
                article_count = int(result[0])
                avg_trust = float(result[1]) if result[1] else 50.0
                avg_bias = float(result[2]) if result[2] else 50.0
                risky_count = int(result[3])

                # Determine risk level from history
                risk_percentage = (risky_count / article_count * 100) if article_count > 0 else 0
                if risk_percentage > 40:
                    risk_level = "HIGH"
                elif risk_percentage > 20:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"

                logger.info(f"📈 Source '{source_domain}': {article_count} articles, trust={avg_trust:.1f}, bias={avg_bias:.1f}")

                return {
                    "domain": source_domain,
                    "article_count": article_count,
                    "avg_trust_score": avg_trust,
                    "avg_bias_score": avg_bias,
                    "risk_level": risk_level,
                    "historical_risk_percentage": round(risk_percentage, 1)
                }

            return {
                "domain": source_domain,
                "article_count": 0,
                "avg_trust_score": 50.0,
                "avg_bias_score": 50.0,
                "risk_level": "UNKNOWN",
                "historical_risk_percentage": 0.0
            }

        except Exception as e:
            logger.error(f"Error retrieving source baseline: {e}")
            return {
                "domain": source_domain,
                "article_count": 0,
                "avg_trust_score": 50.0,
                "avg_bias_score": 50.0,
                "risk_level": "UNKNOWN"
            }

    async def _search_similar_articles(self, article_content: str, top_k: int = 5) -> List[Dict]:
        """Search for similar articles using vector similarity."""
        try:
            # Check if embedding client is available
            if not self.embedding_client:
                logger.warning("Embedding client not available, skipping similarity search")
                return []

            # Generate embedding for the article
            embedding = self.embedding_client.embed_text(article_content)
            if not embedding:
                logger.warning("Failed to generate embedding for similarity search")
                return []

            # Vector similarity search
            query = text("""
                SELECT
                    naa.article_url,
                    naa.article_title,
                    naa.analysis_timestamp,
                    naa.trust_score,
                    (1 - (naa.content_embedding <=> :embedding)) as similarity
                FROM news_article_analyses naa
                WHERE naa.content_embedding IS NOT NULL
                AND (1 - (naa.content_embedding <=> :embedding)) > 0.5
                ORDER BY similarity DESC
                LIMIT :limit
            """)

            results = self.db.execute(query, {
                "embedding": embedding,
                "limit": top_k
            }).fetchall()

            similar_articles = []
            for row in results:
                similar_articles.append({
                    "url": row[0],
                    "title": row[1],
                    "published_at": row[2].isoformat() if row[2] else None,
                    "trust_score": float(row[3]) if row[3] else 50.0,
                    "similarity": float(row[4])
                })

            logger.info(f"Found {len(similar_articles)} similar articles")
            return similar_articles

        except Exception as e:
            logger.error(f"Error searching similar articles: {e}")
            return []

    def close(self):
        """Close database session."""
        if self.db:
            self.db.close()
            logger.info("RAG context service closed")
