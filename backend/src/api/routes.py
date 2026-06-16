"""API routes for NarrativeWatch AI."""

import logging
from typing import Optional, List
from pydantic import BaseModel
from src.agents.orchestrator import get_orchestrator, ContentType

logger = logging.getLogger(__name__)


# ==================== REQUEST/RESPONSE MODELS ====================


class AnalyzePostRequest(BaseModel):
    """Request model for post analysis."""

    post_id: str
    page_username: str
    caption: str
    hashtags: Optional[List[str]] = None
    likes: int = 0
    comments: int = 0


class AnalyzePageRequest(BaseModel):
    """Request model for page analysis."""

    page_id: str
    username: str
    biography: Optional[str] = None
    followers: int = 0


class BiasResultResponse(BaseModel):
    """Bias detection result response."""

    bias_detected: bool
    bias_categories: List[str]
    bias_score: float
    indicators: List[str]
    description: str


class BotResultResponse(BaseModel):
    """Bot detection result response."""

    bot_detected: bool
    bot_score: float
    indicators: List[str]
    engagement_pattern: str
    automation_likelihood: float


class MisinformationResultResponse(BaseModel):
    """Misinformation detection result response."""

    misleading_content: bool
    claim_accuracy: float
    contradictions: List[str]
    verified_claims: List[str]
    research_credibility: str


class AnalysisResponse(BaseModel):
    """Comprehensive analysis response."""

    content_id: str
    content_type: str
    analysis_timestamp: str

    # RAG analysis
    rag_analysis: str
    similar_content_count: int
    coordination_signals: List[str]

    # Research findings
    research_summary: Optional[str]
    credibility_assessment: Optional[str]

    # Individual detections (optional)
    bias_result: Optional[BiasResultResponse] = None
    bot_result: Optional[BotResultResponse] = None
    misinformation_result: Optional[MisinformationResultResponse] = None

    # Aggregated results
    risk_level: str
    risk_score: float
    final_recommendations: List[str]


# ==================== API HANDLERS ====================


class AnalysisAPI:
    """API handler for content analysis."""

    def __init__(self):
        """Initialize API with orchestrator."""
        self.orchestrator = get_orchestrator()
        logger.info("[OK] Analysis API initialized")

    def analyze_post(self, request: AnalyzePostRequest) -> AnalysisResponse:
        """Analyze Instagram post.

        Args:
            request: Post analysis request

        Returns:
            Comprehensive analysis response
        """
        try:
            logger.info(f"API: Analyzing post {request.post_id}")

            # Run orchestrator analysis
            analysis = self.orchestrator.analyze_post(
                post_id=request.post_id,
                page_username=request.page_username,
                caption=request.caption,
                hashtags=request.hashtags,
                likes=request.likes,
                comments=request.comments,
            )

            # Convert to response format
            response = self._convert_analysis_to_response(analysis)
            logger.info(f"[OK] Post analysis complete: {response.risk_level}")
            return response

        except Exception as e:
            logger.error(f"Error analyzing post: {e}")
            raise

    def analyze_page(self, request: AnalyzePageRequest) -> AnalysisResponse:
        """Analyze Instagram page.

        Args:
            request: Page analysis request

        Returns:
            Comprehensive analysis response
        """
        try:
            logger.info(f"API: Analyzing page {request.username}")

            # Run orchestrator analysis
            analysis = self.orchestrator.analyze_page(
                page_id=request.page_id,
                username=request.username,
                biography=request.biography,
                followers=request.followers,
            )

            # Convert to response format
            response = self._convert_analysis_to_response(analysis)
            logger.info(f"[OK] Page analysis complete: {response.risk_level}")
            return response

        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            raise

    def get_rag_stats(self) -> dict:
        """Get RAG pipeline statistics.

        Returns:
            Statistics about RAG database
        """
        try:
            stats = self.orchestrator.pipeline.get_rag_stats()
            logger.info(f"RAG stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return {}

    def health_check(self) -> dict:
        """Check system health.

        Returns:
            Health status of all components
        """
        try:
            health = {
                "status": "healthy",
                "components": {
                    "orchestrator": "ready",
                    "rag_pipeline": "ready",
                    "research_agent": "ready",
                    "rag_agent": "ready",
                    "bias_agent": "pending" if not self.orchestrator.bias_agent else "ready",
                    "bot_agent": "pending" if not self.orchestrator.bot_agent else "ready",
                    "misinformation_agent": "pending"
                    if not self.orchestrator.misinformation_agent
                    else "ready",
                },
            }
            logger.info("Health check complete")
            return health
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    # ==================== HELPERS ====================

    def _convert_analysis_to_response(self, analysis) -> AnalysisResponse:
        """Convert internal analysis to API response."""
        # Convert bias result if present
        bias_response = None
        if analysis.bias_result:
            bias_response = BiasResultResponse(
                bias_detected=analysis.bias_result.bias_detected,
                bias_categories=analysis.bias_result.bias_categories,
                bias_score=analysis.bias_result.bias_score,
                indicators=analysis.bias_result.indicators,
                description=analysis.bias_result.description,
            )

        # Convert bot result if present
        bot_response = None
        if analysis.bot_result:
            bot_response = BotResultResponse(
                bot_detected=analysis.bot_result.bot_detected,
                bot_score=analysis.bot_result.bot_score,
                indicators=analysis.bot_result.indicators,
                engagement_pattern=analysis.bot_result.engagement_pattern,
                automation_likelihood=analysis.bot_result.automation_likelihood,
            )

        # Convert misinformation result if present
        misinformation_response = None
        if analysis.misinformation_result:
            misinformation_response = MisinformationResultResponse(
                misleading_content=analysis.misinformation_result.misleading_content,
                claim_accuracy=analysis.misinformation_result.claim_accuracy,
                contradictions=analysis.misinformation_result.contradictions,
                verified_claims=analysis.misinformation_result.verified_claims,
                research_credibility=analysis.misinformation_result.research_credibility,
            )

        return AnalysisResponse(
            content_id=analysis.content_id,
            content_type=analysis.content_type.value,
            analysis_timestamp=analysis.analysis_timestamp,
            rag_analysis=analysis.rag_analysis,
            similar_content_count=analysis.similar_content_count,
            coordination_signals=analysis.coordination_signals,
            research_summary=analysis.research_summary,
            credibility_assessment=analysis.credibility_assessment,
            bias_result=bias_response,
            bot_result=bot_response,
            misinformation_result=misinformation_response,
            risk_level=analysis.risk_level.value,
            risk_score=analysis.risk_score,
            final_recommendations=analysis.final_recommendations,
        )


def get_analysis_api() -> AnalysisAPI:
    """Get analysis API instance."""
    return AnalysisAPI()
