"""Content Analyzer Agent - Extracts and classifies content."""

from src.agents.base_agent import BaseAgent, AgentConfig
from langchain_core.tools import Tool


class ContentAnalyzerAgent(BaseAgent):
    """Analyzes Instagram content to extract features and classify themes."""

    def __init__(self):
        config = AgentConfig(
            name="content_analyzer",
            description="Analyze Instagram posts to extract content features, emotional language, narrative themes, hashtags, and posting patterns.",
            max_iterations=5,
            temperature=0.3,
        )
        super().__init__(config)

    def _define_tools(self):
        def extract_features(content: str) -> dict:
            return {
                "emotional_language": ["sensational", "fear-inducing"],
                "narrative_themes": ["conspiracy", "distrust"],
                "hashtags": ["#misinformation", "#fake"],
                "posting_frequency": "high",
                "engagement_style": "inflammatory",
            }

        return [
            Tool(
                name="extract_features",
                func=extract_features,
                description="Extract content features and themes",
            ),
        ]

    def _get_system_prompt(self) -> str:
        return """You are the Content Analyzer Agent. Your job is to:
1. Extract key features from Instagram posts/pages
2. Identify emotional language patterns
3. Detect narrative themes
4. Analyze hashtag usage
5. Evaluate posting patterns and frequency

Provide structured analysis of content characteristics."""
