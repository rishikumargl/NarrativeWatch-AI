"""Orchestrator agent that coordinates all analysis agents."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from src.agents.research_agent import ResearchAgent
from src.agents.rag_agent import RAGAgent
from src.database.rag_pipeline import get_rag_pipeline

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ContentType(Enum):
    """Type of content being analyzed."""

    POST = "post"
    PAGE = "page"
    CAMPAIGN = "campaign"


@dataclass
class AnalysisMetadata:
    """Metadata for analysis."""

    content_type: ContentType
    content_id: str
    analyzed_at: str
    agent_versions: Dict[str, str]


@dataclass
class BiasAnalysisResult:
    """Bias detection results."""

    bias_detected: bool
    bias_categories: List[str]
    bias_score: float
    indicators: List[str]
    description: str


@dataclass
class BotAnalysisResult:
    """Bot detection results."""

    bot_detected: bool
    bot_score: float
    indicators: List[str]
    engagement_pattern: str
    automation_likelihood: float


@dataclass
class MisinformationResult:
    """Misinformation detection results."""

    misleading_content: bool
    claim_accuracy: float
    contradictions: List[str]
    verified_claims: List[str]
    research_credibility: str


@dataclass
class ComprehensiveAnalysis:
    """Complete analysis from all agents."""

    content_id: str
    content_type: ContentType
    analysis_timestamp: str

    # RAG analysis
    rag_analysis: str
    similar_content_count: int
    coordination_signals: List[str]

    # Research findings
    research_summary: Optional[str]
    credibility_assessment: Optional[str]

    # Individual agent results (filled by other team members)
    bias_result: Optional[BiasAnalysisResult] = None
    bot_result: Optional[BotAnalysisResult] = None
    misinformation_result: Optional[MisinformationResult] = None

    # Aggregated findings
    risk_level: RiskLevel = RiskLevel.NONE
    risk_score: float = 0.0
    final_recommendations: List[str] = None

    # Metadata
    metadata: Optional[AnalysisMetadata] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.final_recommendations is None:
            self.final_recommendations = []


class Orchestrator:
    """Main orchestrator coordinating all analysis agents."""

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.research_agent = ResearchAgent()
        self.rag_agent = RAGAgent()
        self.pipeline = get_rag_pipeline()

        # Placeholders for agents built by other team members
        self.bias_agent = None  # Team member: ML/NLP specialist
        self.bot_agent = None   # Team member: Data engineer
        self.misinformation_agent = None  # Team member: Data engineer

        logger.info("✓ Orchestrator initialized")

    def analyze_post(
        self,
        post_id: str,
        page_username: str,
        caption: str,
        hashtags: Optional[List[str]] = None,
        likes: int = 0,
        comments: int = 0,
        use_all_agents: bool = True,
    ) -> ComprehensiveAnalysis:
        """Analyze Instagram post comprehensively.

        Orchestrates research, RAG analysis, bias detection, bot detection,
        and misinformation detection.

        Args:
            post_id: Post ID
            page_username: Username of posting page
            caption: Post caption
            hashtags: Post hashtags
            likes: Like count
            comments: Comment count
            use_all_agents: Whether to use all agents

        Returns:
            Comprehensive analysis from all agents
        """
        try:
            logger.info(f"🎯 Orchestrator starting comprehensive analysis for post {post_id}")
            analysis_start = datetime.utcnow().isoformat()

            # 1. RAG Analysis (vector similarity + LLM)
            logger.info("→ Running RAG analysis...")
            rag_result = self.rag_agent.analyze_post(
                post_id=post_id,
                caption=caption,
                hashtags=hashtags,
                use_research=True,
            )

            # 2. Research Analysis (web search)
            logger.info("→ Running research analysis...")
            research_result = None
            if hashtags:
                research_result = self.research_agent.research_narrative(
                    narrative_theme=caption,
                    hashtags=hashtags,
                    depth="standard",
                )

            # 3. Bias Detection (to be implemented by ML/NLP team)
            bias_result = None
            if self.bias_agent and use_all_agents:
                logger.info("→ Running bias detection...")
                try:
                    bias_result = self.bias_agent.detect_bias(caption, hashtags)
                except Exception as e:
                    logger.warning(f"Bias detection unavailable: {e}")

            # 4. Bot Detection (to be implemented by data eng team)
            bot_result = None
            if self.bot_agent and use_all_agents:
                logger.info("→ Running bot detection...")
                try:
                    bot_result = self.bot_agent.detect_bot(
                        page=page_username,
                        engagement=(likes, comments),
                    )
                except Exception as e:
                    logger.warning(f"Bot detection unavailable: {e}")

            # 5. Misinformation Detection (to be implemented by data eng team)
            misinformation_result = None
            if self.misinformation_agent and use_all_agents:
                logger.info("→ Running misinformation detection...")
                try:
                    misinformation_result = self.misinformation_agent.detect_misinformation(
                        caption,
                        hashtags,
                    )
                except Exception as e:
                    logger.warning(f"Misinformation detection unavailable: {e}")

            # 6. Aggregate results
            logger.info("→ Aggregating analysis results...")
            comprehensive = self._aggregate_analysis(
                post_id=post_id,
                content_type=ContentType.POST,
                rag_result=rag_result,
                research_result=research_result,
                bias_result=bias_result,
                bot_result=bot_result,
                misinformation_result=misinformation_result,
                analysis_timestamp=analysis_start,
            )

            logger.info(f"✓ Analysis complete. Risk level: {comprehensive.risk_level.value}")
            return comprehensive

        except Exception as e:
            logger.error(f"Error in orchestrator analysis: {e}")
            raise

    def analyze_page(
        self,
        page_id: str,
        username: str,
        biography: Optional[str] = None,
        followers: int = 0,
        use_all_agents: bool = True,
    ) -> ComprehensiveAnalysis:
        """Analyze Instagram page comprehensively.

        Args:
            page_id: Page ID
            username: Page username
            biography: Page biography
            followers: Follower count
            use_all_agents: Whether to use all agents

        Returns:
            Comprehensive analysis
        """
        try:
            logger.info(f"🎯 Orchestrator starting comprehensive analysis for page {username}")
            analysis_start = datetime.utcnow().isoformat()

            # 1. RAG Analysis
            logger.info("→ Running RAG analysis...")
            rag_result = self.rag_agent.analyze_page(
                page_id=page_id,
                username=username,
                biography=biography,
                use_research=True,
            )

            # 2. Research Analysis
            logger.info("→ Running research analysis...")
            research_result = self.research_agent.get_context_about_page(
                username=username,
                biography=biography,
            )

            # 3. Aggregate results
            comprehensive = self._aggregate_analysis(
                post_id=page_id,
                content_type=ContentType.PAGE,
                rag_result=rag_result,
                research_result=research_result,
                bias_result=None,
                bot_result=None,
                misinformation_result=None,
                analysis_timestamp=analysis_start,
            )

            logger.info(f"✓ Page analysis complete. Risk level: {comprehensive.risk_level.value}")
            return comprehensive

        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            raise

    def register_bias_agent(self, agent):
        """Register bias detection agent."""
        self.bias_agent = agent
        logger.info("✓ Bias detection agent registered")

    def register_bot_agent(self, agent):
        """Register bot detection agent."""
        self.bot_agent = agent
        logger.info("✓ Bot detection agent registered")

    def register_misinformation_agent(self, agent):
        """Register misinformation detection agent."""
        self.misinformation_agent = agent
        logger.info("✓ Misinformation detection agent registered")

    # ==================== HELPERS ====================

    def _aggregate_analysis(
        self,
        post_id: str,
        content_type: ContentType,
        rag_result: Any,
        research_result: Any,
        bias_result: Optional[BiasAnalysisResult],
        bot_result: Optional[BotAnalysisResult],
        misinformation_result: Optional[MisinformationResult],
        analysis_timestamp: str,
    ) -> ComprehensiveAnalysis:
        """Aggregate all analysis results."""
        # Extract RAG findings
        rag_analysis = rag_result.analysis if rag_result else ""
        similar_content = len(rag_result.context.similar_posts) if rag_result else 0
        coordination_signals = rag_result.insights if rag_result else []

        # Extract research findings
        research_summary = None
        credibility = None
        if isinstance(research_result, dict) and "summary" in research_result:
            research_summary = research_result.get("summary")
            credibility = research_result.get("credibility_assessment")
        elif hasattr(research_result, "summary"):
            research_summary = research_result.summary
            credibility = research_result.credibility_assessment

        # Calculate risk level
        risk_level, risk_score = self._calculate_risk_level(
            bias_result=bias_result,
            bot_result=bot_result,
            misinformation_result=misinformation_result,
            rag_confidence=rag_result.confidence_score if rag_result else 0.0,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            bias_result=bias_result,
            bot_result=bot_result,
            misinformation_result=misinformation_result,
            risk_level=risk_level,
            rag_recommendations=rag_result.recommendations if rag_result else [],
        )

        # Create metadata
        metadata = AnalysisMetadata(
            content_type=content_type,
            content_id=post_id,
            analyzed_at=analysis_timestamp,
            agent_versions={
                "research": "1.0",
                "rag": "1.0",
                "bias": "pending",
                "bot": "pending",
                "misinformation": "pending",
            },
        )

        return ComprehensiveAnalysis(
            content_id=post_id,
            content_type=content_type,
            analysis_timestamp=analysis_timestamp,
            rag_analysis=rag_analysis,
            similar_content_count=similar_content,
            coordination_signals=coordination_signals,
            research_summary=research_summary,
            credibility_assessment=credibility,
            bias_result=bias_result,
            bot_result=bot_result,
            misinformation_result=misinformation_result,
            risk_level=risk_level,
            risk_score=risk_score,
            final_recommendations=recommendations,
            metadata=metadata,
        )

    def _calculate_risk_level(
        self,
        bias_result: Optional[BiasAnalysisResult],
        bot_result: Optional[BotAnalysisResult],
        misinformation_result: Optional[MisinformationResult],
        rag_confidence: float,
    ) -> tuple:
        """Calculate overall risk level from individual assessments."""
        risk_score = 0.0
        risk_signals = []

        # Bias signals
        if bias_result and bias_result.bias_detected:
            risk_score += bias_result.bias_score
            risk_signals.append("bias")

        # Bot signals
        if bot_result and bot_result.bot_detected:
            risk_score += bot_result.bot_score
            risk_signals.append("bot")

        # Misinformation signals
        if misinformation_result and misinformation_result.misleading_content:
            risk_score += 1 - misinformation_result.claim_accuracy
            risk_signals.append("misinformation")

        # Normalize risk score
        risk_score = min(1.0, risk_score / max(1, len(risk_signals)))

        # Determine risk level
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        elif risk_score > 0.0:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.NONE

        return risk_level, risk_score

    def _generate_recommendations(
        self,
        bias_result: Optional[BiasAnalysisResult],
        bot_result: Optional[BotAnalysisResult],
        misinformation_result: Optional[MisinformationResult],
        risk_level: RiskLevel,
        rag_recommendations: List[str],
    ) -> List[str]:
        """Generate comprehensive recommendations."""
        recommendations = list(rag_recommendations)  # Start with RAG recommendations

        # Add agent-specific recommendations
        if bias_result and bias_result.bias_detected:
            recommendations.append(f"Address detected bias: {bias_result.bias_categories}")

        if bot_result and bot_result.bot_detected:
            recommendations.append(f"Investigate automated behavior (score: {bot_result.bot_score:.2f})")

        if misinformation_result and misinformation_result.misleading_content:
            recommendations.append("Add fact-check label to content")

        # Risk-level specific recommendations
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("⚠️ ESCALATE: Mark for immediate human review")
            recommendations.append("Consider content removal if violations confirmed")

        elif risk_level == RiskLevel.HIGH:
            recommendations.append("Flag for urgent review")
            recommendations.append("Prioritize in moderation queue")

        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("Queue for standard review")
            recommendations.append("Monitor user for patterns")

        return list(set(recommendations))  # Remove duplicates


def get_orchestrator() -> Orchestrator:
    """Get orchestrator instance."""
    return Orchestrator()
