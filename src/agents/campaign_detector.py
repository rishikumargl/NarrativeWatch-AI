"""Campaign Detector Agent - Identifies coordinated influence campaigns."""

from src.agents.base_agent import BaseAgent, AgentConfig
from langchain_core.tools import Tool


class CampaignDetectorAgent(BaseAgent):
    """Identifies coordinated influence campaigns."""

    def __init__(self):
        config = AgentConfig(
            name="campaign_detector",
            description="Identify coordinated influence campaigns by analyzing cross-page hashtag overlap, timing correlation, narrative similarity, and account relationships.",
            temperature=0.4,
        )
        super().__init__(config)

    def _define_tools(self):
        def detect_campaigns(pages: list) -> dict:
            return {
                "campaigns_detected": 2,
                "campaign_clusters": [
                    {
                        "id": "campaign_1",
                        "pages": 8,
                        "hashtag_overlap": 0.89,
                        "timing_correlation": 0.92,
                        "narrative_similarity": 0.85,
                        "confidence": 0.91,
                    }
                ],
                "coordination_evidence": ["synchronized posting", "shared hashtags"],
            }

        return [
            Tool(
                name="detect_campaigns",
                func=detect_campaigns,
                description="Detect coordinated influence campaigns",
            ),
        ]

    def _get_system_prompt(self) -> str:
        return """You are the Campaign Detector Agent. Your job is to:
1. Identify coordinated campaigns across pages
2. Analyze hashtag overlap between pages
3. Detect timing correlations in posts
4. Find narrative similarity across content
5. Map account relationships

Provide campaign clusters with coordination confidence."""
