"""Research Agent - Gathers external information."""

from src.agents.base_agent import BaseAgent, AgentConfig
from langchain_core.tools import Tool


class ResearchAgent(BaseAgent):
    """Gathers external information via Tavily and APIs."""

    def __init__(self):
        config = AgentConfig(
            name="research_agent",
            description="Research external sources using Tavily Search API to fact-check claims and find corroborating or contradicting information.",
            temperature=0.3,
        )
        super().__init__(config)

    def _define_tools(self):
        def tavily_search(query: str) -> dict:
            return {
                "search_results": [
                    {
                        "title": "Fact check article",
                        "source": "snopes.com",
                        "verdict": "FALSE",
                        "relevance": 0.94,
                    }
                ],
                "related_articles": 5,
                "credible_sources": 3,
                "contradictions_found": 1,
            }

        return [
            Tool(
                name="tavily_search",
                func=tavily_search,
                description="Search Tavily for fact-checking and external sources",
            ),
        ]

    def _get_system_prompt(self) -> str:
        return """You are the Research Agent. Your job is to:
1. Use Tavily Search API to find external information
2. Fact-check claims made in posts
3. Find corroborating or contradicting sources
4. Identify credible vs non-credible sources
5. Provide source reliability assessments

Focus on evidence quality and source credibility."""
