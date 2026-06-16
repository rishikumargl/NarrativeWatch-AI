"""Database module for NarrativeWatch AI."""

from .postgres_client import PostgresClient, get_client, get_session
from .models import (
    InstagramPost,
    InstagramPage,
    Campaign,
    BiasPattern,
    AnalysisResult,
    Base,
)

__all__ = [
    "PostgresClient",
    "get_client",
    "get_session",
    "InstagramPost",
    "InstagramPage",
    "Campaign",
    "BiasPattern",
    "AnalysisResult",
    "Base",
]
