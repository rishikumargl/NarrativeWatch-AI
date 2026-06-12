"""Bot Detector Agent - Analyzes engagement for bot activity."""

from src.agents.base_agent import BaseAgent, AgentConfig
from langchain_core.tools import Tool


class BotDetectorAgent(BaseAgent):
    """Analyzes engagement patterns to detect bot activity."""

    def __init__(self):
        config = AgentConfig(
            name="bot_detector",
            description="Analyze comment patterns, like velocity, follower growth anomalies, and coordinated engagement to detect bot activity.",
            temperature=0.4,
        )
        super().__init__(config)

    def _define_tools(self):
        def analyze_engagement(data: dict) -> dict:
            return {
                "bot_probability": 0.82,
                "suspicious_patterns": [
                    "sudden follower spike",
                    "coordinated comments",
                    "automated engagement",
                ],
                "comment_authenticity": 0.25,
                "like_velocity": "abnormal",
                "engagement_confidence": 0.88,
            }

        return [
            Tool(
                name="analyze_engagement",
                func=analyze_engagement,
                description="Analyze engagement patterns for bot detection",
            ),
        ]

    def _get_system_prompt(self) -> str:
        return """You are the Bot Detector Agent. Your job is to:
1. Analyze comment patterns for automation
2. Detect unusual like velocity
3. Identify follower growth anomalies
4. Find coordinated engagement signals
5. Calculate bot probability scores

Provide bot detection confidence and evidence."""
