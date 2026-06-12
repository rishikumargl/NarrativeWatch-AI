"""Request models for API endpoints."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class AnalyzePageRequest(BaseModel):
    """Request model for analyzing an Instagram page."""

    username: str = Field(..., description="Instagram page username")
    include_posts: bool = Field(
        default=True, description="Whether to analyze posts from the page"
    )
    num_posts: int = Field(
        default=20, ge=1, le=100, description="Number of recent posts to analyze"
    )
    include_campaigns: bool = Field(
        default=True, description="Whether to detect coordinated campaigns"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "username": "example_page",
                "include_posts": True,
                "num_posts": 20,
                "include_campaigns": True,
            }
        }


class AnalyzePostRequest(BaseModel):
    """Request model for analyzing a single Instagram post."""

    post_url: str = Field(..., description="Instagram post URL")
    include_context: bool = Field(
        default=True, description="Include context from page history"
    )
    check_campaigns: bool = Field(
        default=True, description="Check if post is part of a campaign"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "post_url": "https://instagram.com/p/ABC123DEF456/",
                "include_context": True,
                "check_campaigns": True,
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
    """Request model for analyzing multiple pages."""

    pages: List[str] = Field(..., description="List of Instagram usernames")
    detect_coordination: bool = Field(
        default=True, description="Detect coordination between pages"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pages": ["page1", "page2", "page3"],
                "detect_coordination": True,
            }
        }
