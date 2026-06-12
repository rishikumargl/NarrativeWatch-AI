"""FastAPI application for NarrativeWatch AI."""

import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.config import settings
from src.logger import setup_logger
from src.models.request import (
    AnalyzePageRequest,
    AnalyzePostRequest,
    SimilarSearchRequest,
)
from src.models.response import (
    AnalysisResponse,
    PageAnalysisResponse,
    PostAnalysisResponse,
    ErrorResponse,
    HealthCheckResponse,
    WorkflowStatusResponse,
)
from src.workflow.orchestration import orchestration_engine
from src.workflow.state_manager import state_manager
from src.agents.orchestrator import OrchestratorAgent
from src.agents.content_analyzer import ContentAnalyzerAgent
from src.agents.rag_agent import RAGAgent
from src.agents.research_agent import ResearchAgent
from src.agents.bias_detector import BiasDetectorAgent
from src.agents.bot_detector import BotDetectorAgent
from src.agents.campaign_detector import CampaignDetectorAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.agents.reviewer_agent import ReviewerAgent
import asyncio


# Initialize FastAPI app
app = FastAPI(
    title="NarrativeWatch AI",
    description="Multi-Agent Social Media Intelligence Platform",
    version="1.0.0",
)

logger = setup_logger("app")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents (global)
AGENTS = {
    "orchestrator": OrchestratorAgent(),
    "content_analyzer": ContentAnalyzerAgent(),
    "rag_agent": RAGAgent(),
    "research_agent": ResearchAgent(),
    "bias_detector": BiasDetectorAgent(),
    "bot_detector": BotDetectorAgent(),
    "campaign_detector": CampaignDetectorAgent(),
    "synthesis_agent": SynthesisAgent(),
    "reviewer_agent": ReviewerAgent(),
}

# Store workflow results
WORKFLOW_RESULTS = {}


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("NarrativeWatch AI API starting up")
    logger.info(f"Environment: {settings.APP_NAME} v{settings.APP_VERSION}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("NarrativeWatch AI API shutting down")
    state_manager.clear_all_states()


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="ok",
        version=settings.APP_VERSION,
        components={
            "api": "ok",
            "agents": "ok",
            "database": "ok",
        },
    )


@app.post("/analyze/page", response_model=PageAnalysisResponse)
async def analyze_page(request: AnalyzePageRequest, background_tasks: BackgroundTasks):
    """
    Analyze Instagram page.

    Args:
        request: Page analysis request
        background_tasks: Background task queue

    Returns:
        Page analysis result
    """
    try:
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting page analysis: {request.username}")

        # Create workflow
        workflow_id = f"wf_{analysis_id[:8]}"

        # Run analysis in background
        background_tasks.add_task(
            _run_page_analysis, workflow_id, analysis_id, request
        )

        return PageAnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            trust_score=0,
            risk_level="unknown",
            risk_flags=[],
            summary="Analysis in progress",
            page_username=request.username,
            posts_analyzed=request.num_posts,
        )

    except Exception as e:
        logger.error(f"Page analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/post", response_model=PostAnalysisResponse)
async def analyze_post(request: AnalyzePostRequest, background_tasks: BackgroundTasks):
    """
    Analyze single Instagram post.

    Args:
        request: Post analysis request
        background_tasks: Background task queue

    Returns:
        Post analysis result
    """
    try:
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting post analysis: {request.post_url}")

        workflow_id = f"wf_{analysis_id[:8]}"

        # Run analysis in background
        background_tasks.add_task(
            _run_post_analysis, workflow_id, analysis_id, request
        )

        return PostAnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            trust_score=0,
            risk_level="unknown",
            risk_flags=[],
            summary="Analysis in progress",
            post_id="pending",
            page_username="pending",
            content_type="unknown",
        )

    except Exception as e:
        logger.error(f"Post analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{analysis_id}", response_model=AnalysisResponse)
async def get_results(analysis_id: str):
    """
    Get cached analysis results.

    Args:
        analysis_id: Analysis ID

    Returns:
        Analysis result if available
    """
    if analysis_id in WORKFLOW_RESULTS:
        return WORKFLOW_RESULTS[analysis_id]

    # Look in state manager
    for workflow_state in state_manager.states.values():
        if workflow_state.workflow_id.endswith(analysis_id[:8]):
            final_result = workflow_state.final_result or {}
            return AnalysisResponse(
                analysis_id=analysis_id,
                status="completed",
                trust_score=final_result.get("trust_score", 50),
                risk_level=final_result.get("risk_level", "medium"),
                risk_flags=[],
                summary=final_result.get("summary", "Analysis complete"),
            )

    raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")


@app.post("/search/similar", response_model=list)
async def search_similar(request: SimilarSearchRequest):
    """
    Search for similar content in vector database.

    Args:
        request: Search request

    Returns:
        List of similar posts/campaigns
    """
    try:
        logger.info(f"Searching for similar content: {request.query}")

        # Use RAG agent to search
        rag_result = AGENTS["rag_agent"].run(request.query)

        similar_items = rag_result.output.get("similar_posts", [])
        similar_items += rag_result.output.get("similar_campaigns", [])

        return similar_items

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """
    Get workflow execution status.

    Args:
        workflow_id: Workflow ID

    Returns:
        Workflow status
    """
    state = state_manager.get_workflow_state(workflow_id)

    if not state:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    agent_statuses = {
        name: agent_state.status
        for name, agent_state in state.agent_states.items()
    }

    completed_agents = sum(1 for s in agent_statuses.values() if s == "completed")
    total_agents = len(agent_statuses)
    progress = int((completed_agents / total_agents * 100)) if total_agents > 0 else 0

    return WorkflowStatusResponse(
        workflow_id=workflow_id,
        status=state.status,
        agent_statuses=agent_statuses,
        progress_percent=progress,
        error_message=state.error_message,
    )


# Background task functions
async def _run_page_analysis(workflow_id: str, analysis_id: str, request: AnalyzePageRequest):
    """Run page analysis in background."""
    try:
        logger.info(f"Running page analysis for {request.username}")

        # Execute workflow
        state = await orchestration_engine.execute_workflow(
            workflow_id, f"Analyze page: {request.username}", AGENTS
        )

        # Store result
        final_state = state_manager.get_workflow_state(workflow_id)
        WORKFLOW_RESULTS[analysis_id] = PageAnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            trust_score=final_state.final_result.get("trust_score", 50),
            risk_level=final_state.final_result.get("risk_level", "medium"),
            risk_flags=[],
            summary=final_state.final_result.get("summary", "Analysis complete"),
            page_username=request.username,
            posts_analyzed=request.num_posts,
        )

        logger.info(f"Page analysis completed: {analysis_id}")

    except Exception as e:
        logger.error(f"Background analysis error: {e}")


async def _run_post_analysis(workflow_id: str, analysis_id: str, request: AnalyzePostRequest):
    """Run post analysis in background."""
    try:
        logger.info(f"Running post analysis for {request.post_url}")

        # Execute workflow
        state = await orchestration_engine.execute_workflow(
            workflow_id, f"Analyze post: {request.post_url}", AGENTS
        )

        # Store result
        final_state = state_manager.get_workflow_state(workflow_id)
        WORKFLOW_RESULTS[analysis_id] = PostAnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            trust_score=final_state.final_result.get("trust_score", 50),
            risk_level=final_state.final_result.get("risk_level", "medium"),
            risk_flags=[],
            summary=final_state.final_result.get("summary", "Analysis complete"),
            post_id=request.post_url.split("/")[-2],
            page_username="unknown",
            content_type="post",
        )

        logger.info(f"Post analysis completed: {analysis_id}")

    except Exception as e:
        logger.error(f"Background analysis error: {e}")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail, detail=str(exc), request_id=str(uuid.uuid4())
        ).dict(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.API_RELOAD,
    )
