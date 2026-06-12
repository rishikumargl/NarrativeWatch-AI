"""RAG Agent - Retrieves similar historical patterns."""

from src.agents.base_agent import BaseAgent, AgentConfig
from langchain_core.tools import Tool


class RAGAgent(BaseAgent):
    """Retrieves similar posts and campaigns from vector database."""

    def __init__(self):
        config = AgentConfig(
            name="rag_agent",
            description="Query vector database to find similar posts, campaigns, and bias patterns. Use embeddings for semantic similarity search.",
            temperature=0.2,
        )
        super().__init__(config)

    def _define_tools(self):
        def similarity_search(query: str) -> dict:
            return {
                "similar_posts": [
                    {"id": "post_1", "similarity": 0.92, "campaign": "disinformation_2024"},
                ],
                "similar_campaigns": [
                    {"id": "campaign_1", "similarity": 0.88, "pages": 15}
                ],
                "bias_patterns": [
                    {"type": "political", "similarity": 0.85, "frequency": 12}
                ],
            }

        return [
            Tool(
                name="similarity_search",
                func=similarity_search,
                description="Search for similar posts and campaigns in database",
            ),
        ]

    def _get_system_prompt(self) -> str:
        return """You are the RAG Agent. Your job is to:
1. Convert queries to embeddings
2. Search PostgreSQL + pgvector database
3. Retrieve similar historical posts and campaigns
4. Find matching bias patterns
5. Return ranked results by similarity

Use vector similarity for semantic matching."""
