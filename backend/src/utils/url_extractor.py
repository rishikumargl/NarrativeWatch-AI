"""Extract article content from news URLs"""

import logging
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class URLExtractor:
    """Extract article content from news URLs"""

    @staticmethod
    async def extract_article(url: str) -> Dict[str, str]:
        """
        Extract article content from URL

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
            logger.info(f"Extracting article from URL: {url}")

            # Try newspaper3k first (best for news articles)
            article = Article(url)
            article.download()
            article.parse()

            if article.text and len(article.text) > 100:
                logger.info(f"✅ Successfully extracted {len(article.text)} chars from {url}")
                return {
                    "title": article.title or "No Title",
                    "content": article.text,
                    "author": article.authors[0] if article.authors else "Unknown",
                    "publish_date": str(article.publish_date) if article.publish_date else "Unknown",
                    "success": True
                }

            # Fallback to BeautifulSoup if newspaper3k fails
            logger.warning("Newspaper3k extraction failed, trying BeautifulSoup...")
            return URLExtractor._extract_with_beautifulsoup(url)

        except Exception as e:
            logger.error(f"Error extracting from URL: {str(e)}")
            return URLExtractor._extract_with_beautifulsoup(url)

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
                    "content": content[:5000],  # Limit to 5000 chars
                    "author": "Unknown",
                    "publish_date": "Unknown",
                    "success": True
                }
            else:
                logger.warning(f"❌ Could not extract meaningful content from {url}")
                return {
                    "title": "Unable to extract",
                    "content": f"Could not extract article content from: {url}",
                    "author": "Unknown",
                    "publish_date": "Unknown",
                    "success": False
                }

        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed: {str(e)}")
            return {
                "title": "Error",
                "content": f"Error extracting from URL: {str(e)}",
                "author": "Unknown",
                "publish_date": "Unknown",
                "success": False
            }
