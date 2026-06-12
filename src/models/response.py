from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .enums import RiskLevel, BiasType


class FindingDetail(BaseModel):
    agent_name: str = Field(..., description="Name of the analyzing agent")
    category: str = Field(..., description="Category of finding (e.g., 'bias', 'bot', 'manipulation')")
    severity: RiskLevel = Field(..., description="Risk level of the finding")
    description: str = Field(..., description="Detailed description of the finding")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting the finding")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")

    class Config:
        schema_extra = {
            "example": {
                "agent_name": "Bias Detector",
                "category": "political_bias",
                "severity": "high",
                "description": "Detected strong political bias favoring party X",
                "evidence": ["Hashtag analysis shows 85% support tags", "Emotional language indicators"],
                "confidence": 0.92
            }
        }


class AnalysisResponse(BaseModel):
    request_id: str = Field(..., description="Unique identifier for this analysis request")
    instagram_url: str = Field(..., description="URL that was analyzed")
    analysis_type: str = Field(..., description="Type of analysis performed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the analysis was completed")
    trust_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall trust score 0-100 (higher is more trustworthy)"
    )
    risk_level: RiskLevel = Field(..., description="Overall risk assessment")
    findings: List[FindingDetail] = Field(
        default_factory=list,
        description="Detailed findings from each agent"
    )
    summary: str = Field(..., description="Brief summary of analysis results")
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations based on findings"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the analysis"
    )

    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_12345abcde",
                "instagram_url": "https://www.instagram.com/bbcnews/",
                "analysis_type": "page",
                "timestamp": "2026-06-12T10:30:00",
                "trust_score": 75,
                "risk_level": "medium",
                "findings": [
                    {
                        "agent_name": "Content Analyzer",
                        "category": "emotional_manipulation",
                        "severity": "medium",
                        "description": "Detected use of emotional language in 40% of posts",
                        "evidence": ["High exclamation marks", "Urgency indicators"],
                        "confidence": 0.85
                    }
                ],
                "summary": "Page shows moderate risk factors with some political bias indicators",
                "recommendations": ["Cross-verify claims with fact-checkers", "Monitor engagement patterns"],
                "metadata": {"processing_time_seconds": 12.5, "agents_executed": 8}
            }
        }


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Detailed error message")
    request_id: Optional[str] = Field(None, description="Associated request ID if available")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
