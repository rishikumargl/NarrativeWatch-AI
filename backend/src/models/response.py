"""Response models for API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TrustScoreResponse(BaseModel):
    """Response model with trust score."""

    trust_score: int = Field(..., ge=0, le=100, description="Trust score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in the assessment"
    )


class RiskFlagResponse(BaseModel):
    """Model for risk flags in analysis."""

    flag: str = Field(..., description="Type of risk (misinformation, bot, bias, etc)")
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: str = Field(..., description="Details about the risk")


class AnalysisResponse(BaseModel):
    """Base analysis response."""

    analysis_id: str = Field(..., description="Unique analysis ID")
    status: str = Field(..., description="Analysis status (completed, processing, failed)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trust_score: int = Field(..., ge=0, le=100)
    risk_level: str
    risk_flags: List[RiskFlagResponse]
    summary: str = Field(..., description="Brief summary of findings")
    recommendations: List[str] = Field(default_factory=list)


class ArticleAnalysisResponse(AnalysisResponse):
    """Response for news article analysis."""

    article_title: str = Field(..., description="Article title")
    source: str = Field(..., description="News source")
    author: Optional[str] = Field(default=None, description="Article author")
    published_at: Optional[str] = Field(default=None, description="Publication date")
    article_url: Optional[str] = Field(default=None, description="Article URL")
    detected_patterns: Dict[str, Any] = Field(default_factory=dict)
    misinformation_signals: Optional[Dict[str, Any]] = Field(default=None)
    bias_indicators: Optional[Dict[str, Any]] = Field(default=None)


class NewsSearchResponse(BaseModel):
    """Response for news search results."""

    query: str = Field(..., description="Search query used")
    total_results: int = Field(..., description="Total articles found")
    articles_analyzed: int = Field(..., description="Articles in response")
    articles: List[ArticleAnalysisResponse] = Field(
        ..., description="Analyzed articles"
    )
    dominant_narratives: List[str] = Field(default_factory=list)
    coordinated_campaigns: List[Dict[str, Any]] = Field(default_factory=list)
    overall_trust_score: float = Field(
        ..., ge=0.0, le=100.0, description="Average trust score"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Keep aliases for backwards compatibility
PageAnalysisResponse = ArticleAnalysisResponse
PostAnalysisResponse = ArticleAnalysisResponse
UserAnalysisResponse = ArticleAnalysisResponse
TweetAnalysisResponse = ArticleAnalysisResponse


class CampaignAnalysisResponse(BaseModel):
    """Response for campaign detection."""

    campaign_id: str = Field(..., description="Unique campaign ID")
    detected_pages: List[str] = Field(..., description="Pages in the campaign")
    coordination_score: float = Field(
        ..., ge=0.0, le=1.0, description="Campaign coordination confidence"
    )
    hashtags: List[str] = Field(default_factory=list)
    narrative_themes: List[str] = Field(default_factory=list)
    timing_correlation: float = Field(default=0.0)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(default=None)


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status (ok, degraded, down)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")
    components: Dict[str, str] = Field(default_factory=dict)


class WorkflowStatusResponse(BaseModel):
    """Workflow execution status response."""

    workflow_id: str
    status: str = Field(..., description="Status: initialized, running, completed, failed")
    agent_statuses: Dict[str, str] = Field(default_factory=dict)
    progress_percent: int = Field(..., ge=0, le=100)
    estimated_completion: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
