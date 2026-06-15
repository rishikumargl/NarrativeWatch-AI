"""Extract article content from news URLs"""

import logging
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import trafilatura
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class URLExtractor:
    """Extract article content from news URLs"""

    @staticmethod
    async def extract_article(url: str) -> Dict[str, str]:
        """
        Extract article content from URL with 3 fallback strategies

        Returns:
            {
                "title": str,
                "content": str,
                "author": str,
                "publish_date": str,
                "success": bool
            }
        """
        try:
            logger.info(f"🔗 Extracting article from URL: {url}")

            # Strategy 1: Try Trafilatura (best for news articles)
            logger.info("📖 Strategy 1: Trying Trafilatura...")
            result = URLExtractor._extract_with_trafilatura(url)
            if result["success"]:
                logger.info(f"✅ Trafilatura extracted {len(result['content'])} chars")
                return result

            # Strategy 2: Try newspaper3k (fallback)
            logger.warning("⚠️ Trafilatura failed, trying newspaper3k...")
            result = URLExtractor._extract_with_newspaper(url)
            if result["success"]:
                logger.info(f"✅ newspaper3k extracted {len(result['content'])} chars")
                return result

            # Strategy 3: Try BeautifulSoup (last resort)
            logger.warning("⚠️ newspaper3k failed, trying BeautifulSoup...")
            result = URLExtractor._extract_with_beautifulsoup(url)
            if result["success"]:
                logger.info(f"✅ BeautifulSoup extracted {len(result['content'])} chars")
                return result

            # All failed - return error with URL text
            logger.error(f"❌ All extraction methods failed for {url}")
            return {
                "title": "Article Extraction Failed",
                "content": f"Could not extract content from {url}. URL may be blocked or invalid.",
                "author": "Unknown",
                "publish_date": "Unknown",
                "success": False
            }

        except Exception as e:
            logger.error(f"❌ Critical error in URL extraction: {str(e)}")
            return {
                "title": "Article Extraction Error",
                "content": f"Error extracting from {url}: {str(e)}",
                "author": "Unknown",
                "publish_date": "Unknown",
                "success": False
            }

    @staticmethod
    def _extract_with_trafilatura(url: str) -> Dict[str, str]:
        """Extract using Trafilatura (best for news articles)"""
        try:
            logger.info(f"Trafilatura: Fetching {url}")
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                logger.warning(f"Trafilatura: Failed to fetch {url}")
                return {"success": False, "content": "", "title": "", "author": "", "publish_date": ""}

            result = trafilatura.extract(downloaded, include_comments=False, with_metadata=True)
            if not result:
                logger.warning(f"Trafilatura: No content extracted from {url}")
                return {"success": False, "content": "", "title": "", "author": "", "publish_date": ""}

            # Get metadata
            metadata = trafilatura.extract_metadata(downloaded)

            content = trafilatura.extract(downloaded, include_comments=False)
            title = metadata.title if metadata and metadata.title else "No Title"
            author = metadata.author if metadata and metadata.author else "Unknown"
            date = str(metadata.date) if metadata and metadata.date else "Unknown"

            if content and len(content) > 100:
                logger.info(f"✅ Trafilatura success: {len(content)} chars")
                return {
                    "title": title,
                    "content": content,
                    "author": author,
                    "publish_date": date,
                    "success": True
                }
            return {"success": False, "content": "", "title": "", "author": "", "publish_date": ""}

        except Exception as e:
            logger.debug(f"Trafilatura error: {str(e)}")
            return {"success": False, "content": "", "title": "", "author": "", "publish_date": ""}

    @staticmethod
    def _extract_with_newspaper(url: str) -> Dict[str, str]:
        """Extract using newspaper3k"""
        try:
            logger.info(f"newspaper3k: Fetching {url}")
            article = Article(url)
            article.download()
            article.parse()

            if article.text and len(article.text) > 100:
                logger.info(f"✅ newspaper3k success: {len(article.text)} chars")
                return {
                    "title": article.title or "No Title",
                    "content": article.text,
                    "author": article.authors[0] if article.authors else "Unknown",
                    "publish_date": str(article.publish_date) if article.publish_date else "Unknown",
                    "success": True
                }
            return {"success": False, "content": "", "title": "", "author": "", "publish_date": ""}

        except Exception as e:
            logger.debug(f"newspaper3k error: {str(e)}")
            return {"success": False, "content": "", "title": "", "author": "", "publish_date": ""}

    @staticmethod
    def _extract_with_beautifulsoup(url: str) -> Dict[str, str]:
        """Fallback extraction using BeautifulSoup"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract meta tags as minimal fallback
            meta_title = soup.find('meta', property='og:title')
            meta_description = soup.find('meta', property='og:description')

            if meta_title and meta_description:
                logger.info("📋 Extracted from meta tags (og:title, og:description)")
                return {
                    "title": meta_title.get('content', ''),
                    "content": meta_description.get('content', ''),
                    "author": "Unknown",
                    "publish_date": "Unknown",
                    "success": True
                }

            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()

            # Extract title
            title = "No Title"
            if soup.title:
                title = soup.title.string
            elif soup.find('h1'):
                title = soup.find('h1').get_text()

            # Extract main content
            # Try common article containers
            content_selectors = [
                'article',
                'main',
                '[role="main"]',
                '.article-content',
                '.post-content',
                '.entry-content',
                '[class*="content"]'
            ]

            content_elem = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    break

            if not content_elem:
                content_elem = soup.body if soup.body else soup

            # Extract paragraphs
            paragraphs = content_elem.find_all('p')
            content = '\n'.join([p.get_text() for p in paragraphs if p.get_text().strip()])

            # If no content found, use all text
            if not content or len(content) < 100:
                content = soup.get_text()

            # Clean up whitespace
            content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])

            if len(content) > 100:
                logger.info(f"✅ BeautifulSoup extracted {len(content)} chars from {url}")
                return {
                    "title": title,
                    "content": content,
                    "author": "Unknown",
                    "publish_date": "Unknown",
                    "success": True
                }
            else:
                logger.warning(f"❌ Could not extract meaningful content from {url}")
                return {"success": False, "content": "", "title": "", "author": "", "publish_date": ""}

        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed: {str(e)}")
            return {"success": False, "content": "", "title": "", "author": "", "publish_date": ""}
