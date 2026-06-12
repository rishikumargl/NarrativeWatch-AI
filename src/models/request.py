from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional
from .enums import AnalysisType


class AnalysisRequest(BaseModel):
    instagram_url: str = Field(
        ...,
        description="Instagram page or post URL to analyze"
    )
    analysis_type: AnalysisType = Field(
        default=AnalysisType.PAGE,
        description="Type of analysis: page, post, or account"
    )
    include_historical: bool = Field(
        default=True,
        description="Include historical data in analysis"
    )
    include_bot_analysis: bool = Field(
        default=True,
        description="Perform bot activity detection"
    )
    include_bias_detection: bool = Field(
        default=True,
        description="Perform bias detection analysis"
    )
    include_campaign_detection: bool = Field(
        default=True,
        description="Detect coordinated campaigns"
    )

    @validator("instagram_url")
    def validate_instagram_url(cls, v):
        if not v or not ("instagram.com" in v.lower()):
            raise ValueError("Invalid Instagram URL")
        return v

    class Config:
        schema_extra = {
            "example": {
                "instagram_url": "https://www.instagram.com/bbcnews/",
                "analysis_type": "page",
                "include_historical": True,
                "include_bot_analysis": True,
                "include_bias_detection": True,
                "include_campaign_detection": True,
            }
        }
