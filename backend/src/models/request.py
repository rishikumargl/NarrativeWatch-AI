"""Request models for API endpoints."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class AnalyzeArticleRequest(BaseModel):
    """Request model for analyzing a news article."""

    title: str = Field(..., description="Article title")
    description: Optional[str] = Field(
        default=None, description="Article description"
    )
    content: str = Field(..., description="Article full content")
    source: str = Field(..., description="News source (e.g., 'BBC News')")
    author: Optional[str] = Field(default=None, description="Article author")
    published_at: Optional[str] = Field(
        default=None, description="Publication date (ISO format)"
    )
    url: Optional[str] = Field(default=None, description="Article URL")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Breaking: Major Discovery",
                "description": "Scientists announce breakthrough",
                "content": "Full article content here...",
                "source": "BBC News",
                "author": "John Doe",
                "published_at": "2024-06-12T10:30:00Z",
                "url": "https://bbc.com/news/...",
            }
        }


class SearchNewsRequest(BaseModel):
    """Request model for searching news articles."""

    query: str = Field(..., description="Search query (keywords, topics)")
    num_articles: int = Field(
        default=10, ge=1, le=100, description="Number of articles to fetch"
    )
    sort_by: str = Field(
        default="publishedAt",
        description="Sort order: relevancy, popularity, publishedAt",
    )
    language: str = Field(
        default="en", description="Language code (e.g., en, es, fr)"
    )
    detect_misinformation: bool = Field(
        default=True, description="Whether to detect misinformation"
    )
    detect_bias: bool = Field(
        default=True, description="Whether to detect bias"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "election 2024",
                "num_articles": 20,
                "sort_by": "publishedAt",
                "language": "en",
                "detect_misinformation": True,
                "detect_bias": True,
            }
        }


class SimilarSearchRequest(BaseModel):
    """Request model for searching similar content."""

    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max results to return")
    similarity_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum similarity score"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Find similar misinformation campaigns",
                "limit": 10,
                "similarity_threshold": 0.7,
            }
        }


class BulkAnalysisRequest(BaseModel):
    """Request model for analyzing multiple articles."""

    queries: List[str] = Field(..., description="List of search queries")
    articles_per_query: int = Field(
        default=5, ge=1, le=50, description="Articles to fetch per query"
    )
    detect_coordination: bool = Field(
        default=True, description="Detect coordinated narratives"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "queries": ["election", "vaccine", "climate"],
                "articles_per_query": 5,
                "detect_coordination": True,
            }
        }
