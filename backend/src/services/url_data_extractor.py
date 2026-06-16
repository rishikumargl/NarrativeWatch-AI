"""Enhanced URL data extraction with entities and source metadata."""

import logging
from typing import Dict, Optional
from urllib.parse import urlparse
from src.utils.url_extractor import URLExtractor
from src.utils.entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)


class URLDataExtractor:
    """Extract complete article data including content, entities, and source metadata."""

    @staticmethod
    async def extract_with_entities(url: str) -> Dict:
        """
        Extract article content and enrich with entity extraction.

        Returns:
            {
                "url": str,
                "title": str,
                "content": str,
                "author": str,
                "publish_date": str,
                "source_domain": str,
                "entities": {
                    "total_count": int,
                    "entities": list[{name, type, frequency, importance_score}],
                    "summary": str
                },
                "content_length": int,
                "success": bool,
                "error": Optional[str]
            }
        """
        try:
            logger.info(f"🔗 Extracting data from URL: {url}")

            # Step 1: Extract article content
            extracted = await URLExtractor.extract_article(url)

            if not extracted.get("success"):
                logger.warning(f"Failed to extract content from {url}")
                return {
                    "url": url,
                    "title": "Extraction Failed",
                    "content": "",
                    "author": "",
                    "publish_date": "",
                    "source_domain": URLDataExtractor._get_domain(url),
                    "entities": {"total_count": 0, "entities": [], "summary": ""},
                    "content_length": 0,
                    "success": False,
                    "error": "Failed to extract article content"
                }

            article_content = extracted.get("content", "")
            article_title = extracted.get("title", "No Title")

            # Step 2: Extract entities from content
            logger.info("Extracting entities from article...")
            entities_result = await EntityExtractor.extract_and_score_entities(article_content)

            # Step 3: Get source domain
            source_domain = URLDataExtractor._get_domain(url)

            logger.info(f"✅ Extracted data: {article_title[:50]}... | {len(article_content)} chars | {entities_result['total_count']} entities | from {source_domain}")

            return {
                "url": url,
                "title": article_title,
                "content": article_content,
                "author": extracted.get("author", "Unknown"),
                "publish_date": extracted.get("publish_date", "Unknown"),
                "source_domain": source_domain,
                "entities": entities_result,
                "content_length": len(article_content),
                "success": True,
                "error": None
            }

        except Exception as e:
            logger.error(f"❌ Error in URL data extraction: {str(e)}")
            return {
                "url": url,
                "title": "Extraction Error",
                "content": "",
                "author": "",
                "publish_date": "",
                "source_domain": URLDataExtractor._get_domain(url),
                "entities": {"total_count": 0, "entities": [], "summary": ""},
                "content_length": 0,
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def _get_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain
        except Exception as e:
            logger.error(f"Failed to parse domain from {url}: {e}")
            return "unknown"
