"""Agents module for NarrativeWatch AI."""

from src.agents.base_agent import BaseAgent, AgentConfig
from src.agents.orchestrator import OrchestratorAgent
from src.agents.content_analyzer import ContentAnalyzerAgent
from src.agents.rag_agent import RAGAgent
from src.agents.research_agent import ResearchAgent
from src.agents.bias_detector import BiasDetectorAgent
from src.agents.sentiment_analyzer import SentimentAnalyzerAgent
from src.agents.narrative_tracker import NarrativeTrackerAgent
from src.agents.bot_detector import BotDetectorAgent
from src.agents.campaign_detector import CampaignDetectorAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.agents.reviewer_agent import ReviewerAgent

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "OrchestratorAgent",
    "ContentAnalyzerAgent",
    "RAGAgent",
    "ResearchAgent",
    "BiasDetectorAgent",
    "SentimentAnalyzerAgent",
    "NarrativeTrackerAgent",
    "BotDetectorAgent",
    "CampaignDetectorAgent",
    "SynthesisAgent",
    "ReviewerAgent",
]
