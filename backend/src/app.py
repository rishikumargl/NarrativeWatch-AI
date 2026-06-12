"""FastAPI application for NarrativeWatch AI."""

import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.config import settings
from src.logger import setup_logger
from src.models.request import (
    AnalyzeArticleRequest,
    SearchNewsRequest,
    SimilarSearchRequest,
)
from src.models.response import (
    AnalysisResponse,
    ArticleAnalysisResponse,
    NewsSearchResponse,
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


@app.post("/analyze/article", response_model=ArticleAnalysisResponse)
async def analyze_article(request: AnalyzeArticleRequest, background_tasks: BackgroundTasks):
    """
    Analyze a news article for misinformation, bias, and narrative themes.

    Args:
        request: Article analysis request
        background_tasks: Background task queue

    Returns:
        Article analysis result
    """
    try:
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting article analysis: {request.title[:50]}")

        # Create workflow
        workflow_id = f"wf_{analysis_id[:8]}"

        # Run analysis in background
        background_tasks.add_task(
            _run_article_analysis, workflow_id, analysis_id, request
        )

        return ArticleAnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            trust_score=50,
            risk_level="unknown",
            risk_flags=[],
            summary="Analysis in progress",
            article_title=request.title,
            source=request.source,
        )

    except Exception as e:
        logger.error(f"Article analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/news", response_model=NewsSearchResponse)
async def search_news(request: SearchNewsRequest, background_tasks: BackgroundTasks):
    """
    Search for news articles and analyze them.

    Args:
        request: News search request
        background_tasks: Background task queue

    Returns:
        News search results with analysis
    """
    try:
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting news search: {request.query}")

        workflow_id = f"wf_{analysis_id[:8]}"

        # Run search in background
        background_tasks.add_task(
            _run_news_search, workflow_id, analysis_id, request
        )

        return NewsSearchResponse(
            query=request.query,
            total_results=0,
            articles_analyzed=0,
            articles=[],
            overall_trust_score=50,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"News search error: {e}")
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
def _run_article_analysis(workflow_id: str, analysis_id: str, request: AnalyzeArticleRequest):
    """Run article analysis in background (sync wrapper)."""
    try:
        import asyncio
        logger.info(f"Running article analysis: {request.title[:50]}")

        # Execute workflow - proper async handling
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        state = loop.run_until_complete(
            orchestration_engine.execute_workflow(
                workflow_id, f"Analyze article: {request.title}", AGENTS
            )
        )

        # Store result
        final_state = state_manager.get_workflow_state(workflow_id)
        WORKFLOW_RESULTS[analysis_id] = ArticleAnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            trust_score=final_state.final_result.get("trust_score", 50),
            risk_level=final_state.final_result.get("risk_level", "medium"),
            risk_flags=[],
            summary=final_state.final_result.get("summary", "Analysis complete"),
            article_title=request.title,
            source=request.source,
            author=request.author,
            published_at=request.published_at,
            article_url=request.url,
        )

        logger.info(f"Article analysis completed: {analysis_id}")

    except Exception as e:
        logger.error(f"Background analysis error: {e}")


def _run_news_search(workflow_id: str, analysis_id: str, request: SearchNewsRequest):
    """Run news search and analysis in background (sync wrapper)."""
    try:
        import asyncio
        from src.integrations.newsapi_client import NewsAPIClient

        logger.info(f"Running news search: {request.query}")

        # Fetch articles from NewsAPI
        client = NewsAPIClient()
        articles = client.search_articles(
            query=request.query,
            num_articles=request.num_articles,
            sort_by=request.sort_by,
            language=request.language,
        )

        logger.info(f"Found {len(articles)} articles for query: {request.query}")

        # Execute workflow for analysis
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        state = loop.run_until_complete(
            orchestration_engine.execute_workflow(
                workflow_id, f"Analyze news: {request.query}", AGENTS
            )
        )

        # Store result
        final_state = state_manager.get_workflow_state(workflow_id)

        # Analyze each article
        analyzed_articles = []
        for article in articles:
            analysis_result = ArticleAnalysisResponse(
                analysis_id=f"{analysis_id}_{len(analyzed_articles)}",
                status="completed",
                trust_score=final_state.final_result.get("trust_score", 50),
                risk_level=final_state.final_result.get("risk_level", "medium"),
                risk_flags=[],
                summary=f"Analysis of {article.get('source')}",
                article_title=article.get("title", ""),
                source=article.get("source", ""),
                author=article.get("author", ""),
                published_at=article.get("published_at", ""),
                article_url=article.get("url", ""),
            )
            analyzed_articles.append(analysis_result)

        # Store comprehensive result
        WORKFLOW_RESULTS[analysis_id] = NewsSearchResponse(
            query=request.query,
            total_results=len(articles),
            articles_analyzed=len(analyzed_articles),
            articles=analyzed_articles,
            overall_trust_score=final_state.final_result.get("trust_score", 50),
        )

        logger.info(f"News search completed: {analysis_id}")

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
