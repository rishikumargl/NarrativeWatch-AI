from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from datetime import datetime
import time
import logging

from src.models import AnalysisRequest, AnalysisResponse, ErrorResponse, HealthResponse
from src.utils import generate_request_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NarrativeWatch AI",
    description="Multi-Agent Social Media Intelligence Platform for detecting misleading content, bias, and influence campaigns",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    return response


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@app.get("/api/health", response_model=HealthResponse, tags=["Status"])
async def api_health_check():
    """API health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


# ============================================================================
# Analysis Endpoints
# ============================================================================

@app.post("/api/v1/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_instagram(request: AnalysisRequest):
    """
    Analyze Instagram page/post for misinformation, bias, and coordination.

    This endpoint orchestrates a multi-agent workflow that:
    1. Extracts and analyzes content features
    2. Performs RAG-based historical pattern matching
    3. Conducts external research via Tavily
    4. Detects bias and ideological slant
    5. Analyzes engagement for bot activity
    6. Identifies coordinated campaigns
    7. Synthesizes findings into a coherent report
    8. Quality assurance via reviewer agent
    """
    request_id = generate_request_id()
    logger.info(f"Analysis request {request_id}: {request.instagram_url}")

    try:
        # TODO: Integrate with WorkflowOrchestrator from Team 1
        # For now, return mock response structure
        response = await _mock_analysis(request, request_id)
        logger.info(f"Analysis {request_id} completed successfully")
        return response

    except Exception as e:
        logger.error(f"Analysis {request_id} failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/api/v1/results/{request_id}", response_model=AnalysisResponse, tags=["Analysis"])
async def get_analysis_result(request_id: str):
    """
    Retrieve previously cached analysis results

    In production, this would fetch from a cache/database
    """
    # TODO: Implement caching layer with Redis or database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Result caching not yet implemented"
    )


@app.post("/api/v1/batch-analyze", tags=["Analysis"])
async def batch_analyze(requests: list[AnalysisRequest]):
    """
    Analyze multiple Instagram pages/posts in batch

    Returns list of analysis results
    """
    # TODO: Implement batch processing with job queue
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Batch analysis not yet implemented"
    )


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="validation_error",
            detail=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="http_error",
            detail=exc.detail,
            timestamp=datetime.utcnow()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_server_error",
            detail="An unexpected error occurred",
            timestamp=datetime.utcnow()
        ).dict()
    )


# ============================================================================
# Mock Analysis (for testing/demo)
# ============================================================================

async def _mock_analysis(request: AnalysisRequest, request_id: str) -> AnalysisResponse:
    """
    Mock analysis response for testing

    Replace this with actual WorkflowOrchestrator integration
    """
    from src.models import FindingDetail, RiskLevel

    return AnalysisResponse(
        request_id=request_id,
        instagram_url=request.instagram_url,
        analysis_type=request.analysis_type.value,
        timestamp=datetime.utcnow(),
        trust_score=72.5,
        risk_level=RiskLevel.MEDIUM,
        findings=[
            FindingDetail(
                agent_name="Content Analyzer",
                category="emotional_manipulation",
                severity=RiskLevel.MEDIUM,
                description="Detected use of emotional language in 35% of posts",
                evidence=[
                    "High exclamation marks (avg 2.3 per post)",
                    "Urgency indicators found in 30% of captions",
                    "Fear-based language patterns detected"
                ],
                confidence=0.87
            ),
            FindingDetail(
                agent_name="Bias Detector",
                category="political_bias",
                severity=RiskLevel.LOW,
                description="Slight political lean detected toward progressive viewpoints",
                evidence=[
                    "Hashtag analysis shows 65% progressive-aligned tags",
                    "Language patterns align with progressive rhetoric",
                    "Source selection shows 70% progressive sources"
                ],
                confidence=0.72
            ),
            FindingDetail(
                agent_name="Bot Detector",
                category="bot_activity",
                severity=RiskLevel.LOW,
                description="Minimal bot activity detected in engagement",
                evidence=[
                    "Comment timing appears natural",
                    "Engagement velocity within normal parameters",
                    "Follower growth rate: 2.1% monthly (typical)"
                ],
                confidence=0.91
            )
        ],
        summary="Page shows moderate manipulation tactics with some political bias. Overall engagement appears authentic with minimal bot activity.",
        recommendations=[
            "Cross-verify major claims with fact-checkers",
            "Monitor for changes in posting frequency",
            "Compare narrative consistency with other pages"
        ],
        metadata={
            "processing_time_seconds": 8.432,
            "agents_executed": 8,
            "data_sources_queried": 12,
            "reflection_loop_iterations": 1
        }
    )


# ============================================================================
# Static Files (React Frontend)
# ============================================================================

try:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
except RuntimeError:
    logger.warning("Frontend dist not found. React app not mounted.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
