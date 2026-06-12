"""Request models for API endpoints."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class AnalyzeUserRequest(BaseModel):
    """Request model for analyzing a Twitter user."""

    username: str = Field(..., description="Twitter username (handle without @)")
    include_tweets: bool = Field(
        default=True, description="Whether to analyze tweets from the user"
    )
    num_tweets: int = Field(
        default=20, ge=1, le=100, description="Number of recent tweets to analyze"
    )
    include_campaigns: bool = Field(
        default=True, description="Whether to detect coordinated campaigns"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "username": "example_user",
                "include_tweets": True,
                "num_tweets": 20,
                "include_campaigns": True,
            }
        }


class AnalyzeTweetRequest(BaseModel):
    """Request model for analyzing a single Twitter tweet."""

    tweet_id: str = Field(..., description="Twitter tweet ID")
    include_context: bool = Field(
        default=True, description="Include context from user history"
    )
    check_campaigns: bool = Field(
        default=True, description="Check if tweet is part of a campaign"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tweet_id": "1234567890123456789",
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
    """Request model for analyzing multiple users."""

    users: List[str] = Field(..., description="List of Twitter usernames")
    detect_coordination: bool = Field(
        default=True, description="Detect coordination between users"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "users": ["user1", "user2", "user3"],
                "detect_coordination": True,
            }
        }
