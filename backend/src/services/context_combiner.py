"""Context combination service to merge all data sources."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextCombiner:
    """Combine URL data, RAG context, and news API results into unified bundle."""

    @staticmethod
    def combine_contexts(
        url_data: Dict,
        rag_context: Dict,
        news_api_results: Dict
    ) -> Dict:
        """
        Combine all three data sources into single enriched context.

        Args:
            url_data: From URLDataExtractor
            rag_context: From RAGContextService
            news_api_results: From cross_source_verification

        Returns:
            Unified context bundle for agents
        """
        try:
            logger.info("🔀 Combining all context sources...")

            # Build entity context from both URL extraction and RAG history
            entity_context = ContextCombiner._build_entity_context(
                url_data.get("entities", {}),
                rag_context.get("entity_reputation", {})
            )

            # Build source context
            source_context = {
                "source_domain": url_data.get("source_domain", "unknown"),
                "article_url": url_data.get("url", ""),
                **rag_context.get("source_baseline", {})
            }

            # Build news coverage context
            coverage_context = {
                "similar_articles_found": len(news_api_results.get("matching_sources", [])),
                "verification_score": news_api_results.get("confidence_score", 0),
                "confidence_level": news_api_results.get("confidence_level", "UNKNOWN"),
                "corroborating_sources": [
                    {
                        "source_name": src.get("source", "Unknown"),
                        "title": src.get("title", ""),
                        "url": src.get("url", ""),
                        "published_at": src.get("published_at", "")
                    }
                    for src in news_api_results.get("matching_sources", [])[:5]
                ],
                "verification_details": news_api_results.get("verification_details", []),
                "recommendation": news_api_results.get("recommendation", "")
            }

            # Build contextual summary for agents
            context_summary = ContextCombiner._generate_context_summary(
                url_data,
                entity_context,
                source_context,
                coverage_context
            )

            enriched_context = {
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "data_sources": ["URL", "RAG", "NewsAPI/Tavily"],
                    "total_entities": entity_context.get("total_count", 0),
                    "total_similar_articles": rag_context.get("total_context_items", 0),
                    "total_corroborating_sources": len(news_api_results.get("matching_sources", []))
                },
                "article": {
                    "url": url_data.get("url", ""),
                    "title": url_data.get("title", ""),
                    "content_length": url_data.get("content_length", 0),
                    "author": url_data.get("author", "Unknown"),
                    "publish_date": url_data.get("publish_date", "Unknown")
                },
                "entities": entity_context,
                "source": source_context,
                "news_coverage": coverage_context,
                "rag_history": {
                    "similar_articles": rag_context.get("similar_articles", []),
                    "historical_context_items": rag_context.get("total_context_items", 0)
                },
                "context_summary": context_summary
            }

            logger.info(f"✅ Context combined: {entity_context.get('total_count', 0)} entities | {coverage_context['similar_articles_found']} corroborating sources | {len(rag_context.get('similar_articles', []))} similar historical articles")

            return enriched_context

        except Exception as e:
            logger.error(f"❌ Error combining contexts: {str(e)}")
            # Return minimal valid context structure
            return {
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "data_sources": [],
                    "error": str(e)
                },
                "article": {
                    "url": url_data.get("url", ""),
                    "title": url_data.get("title", ""),
                    "content_length": 0
                },
                "entities": {"total_count": 0, "entities": [], "key_entities": []},
                "source": {"domain": "unknown"},
                "news_coverage": {"similar_articles_found": 0, "verification_score": 0},
                "rag_history": {"similar_articles": []},
                "context_summary": "Error during context combination"
            }

    @staticmethod
    def _build_entity_context(url_entities: Dict, rag_entity_reputation: Dict) -> Dict:
        """Build comprehensive entity context from URL and RAG data."""
        try:
            # Start with URL-extracted entities
            entities_list = url_entities.get("entities", [])

            # Enhance with RAG reputation data
            enriched_entities = []
            for entity in entities_list:
                entity_name = entity.get("name", "")
                rag_data = rag_entity_reputation.get(entity_name, {})

                enriched = {
                    **entity,
                    "historical_mentions": rag_data.get("mention_count", 0),
                    "historical_trust_avg": rag_data.get("avg_trust_in_context", None),
                    "historical_bias_avg": rag_data.get("avg_bias_when_mentioned", None)
                }
                enriched_entities.append(enriched)

            # Sort by importance and limit
            enriched_entities.sort(
                key=lambda x: x.get("importance_score", 0),
                reverse=True
            )

            key_entities = [
                {"name": e.get("name"), "type": e.get("type")}
                for e in enriched_entities[:5]
            ]

            return {
                "total_count": len(enriched_entities),
                "entities": enriched_entities,
                "key_entities": key_entities,
                "summary": url_entities.get("summary", "")
            }

        except Exception as e:
            logger.error(f"Error building entity context: {e}")
            return {"total_count": 0, "entities": [], "key_entities": []}

    @staticmethod
    def _generate_context_summary(url_data: Dict, entity_ctx: Dict, source_ctx: Dict, coverage_ctx: Dict) -> str:
        """Generate natural language summary of combined context."""
        try:
            parts = []

            # Article overview
            parts.append(f"Article: '{url_data.get('title', 'Unknown')}' from {source_ctx.get('source_domain', 'unknown')} ({url_data.get('content_length', 0)} chars)")

            # Entity summary
            if entity_ctx.get("total_count", 0) > 0:
                key_entities = ", ".join([e["name"] for e in entity_ctx.get("key_entities", [])[:3]])
                parts.append(f"Key entities: {key_entities}")

            # Source credibility
            source_trust = source_ctx.get("avg_trust_score", 50)
            parts.append(f"Source historical credibility: {source_trust:.1f}/100 (risk: {source_ctx.get('risk_level', 'UNKNOWN')})")

            # Cross-source coverage
            coverage_score = coverage_ctx.get("verification_score", 0)
            num_sources = coverage_ctx.get("similar_articles_found", 0)
            parts.append(f"Cross-source verification: {num_sources} outlets reporting similar story (confidence: {coverage_ctx.get('confidence_level', 'UNKNOWN')})")

            # Historical context
            similar_count = len(coverage_ctx.get("corroborating_sources", []))
            if similar_count > 0:
                parts.append(f"Similar articles in history: {similar_count} found")

            return " | ".join(parts)

        except Exception as e:
            logger.error(f"Error generating context summary: {e}")
            return "Context summary unavailable"
