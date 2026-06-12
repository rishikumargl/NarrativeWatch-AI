"""Narrative Tracker Agent - Detects and tracks narrative patterns."""

from src.agents.base_agent import BaseAgent, AgentConfig


class NarrativeTrackerAgent(BaseAgent):
    """Detects and tracks narrative patterns across articles."""

    def __init__(self):
        config = AgentConfig(
            name="narrative_tracker",
            description="Identify narrative patterns, story arcs, and thematic consistency across articles. Track how narratives evolve and spread.",
            temperature=0.6,
        )
        super().__init__(config)

    def track_narrative(self, articles: list) -> dict:
        """Track narrative patterns across articles."""
        article_text = "\n\n".join([f"Article {i+1}: {article}" for i, article in enumerate(articles)])

        result = self.run(f"""Analyze the narrative patterns in these articles:

{article_text}

Provide:
1. Common narrative themes
2. Story arc progression
3. Character/entity roles
4. Narrative consistency checks
5. Pattern evolution over time
6. Narrative trust score (0-1)""")
        return result
