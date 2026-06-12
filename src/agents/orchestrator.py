"""Orchestrator Agent - Coordinates all specialized agents."""

from typing import Any, Optional
from src.agents.base_agent import BaseAgent, AgentConfig, AgentResult
from src.logger import setup_logger


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent - Routes and coordinates all specialized agents.

    Responsibilities:
    - Parse user input (Instagram URL/username)
    - Determine required agents based on query
    - Manage execution order and dependencies
    - Aggregate results from all agents
    - Handle errors and retries
    """

    def __init__(self):
        """Initialize OrchestratorAgent."""
        config = AgentConfig(
            name="orchestrator",
            description="""You are the Orchestrator Agent for NarrativeWatch AI.
Your role is to:
1. Parse user queries about Instagram pages/posts
2. Determine which specialized agents should be executed
3. Coordinate their execution in optimal order
4. Aggregate and synthesize their findings
5. Guide the workflow through completion

You have access to these agents:
- ContentAnalyzer: Extracts and classifies post content
- RAG: Retrieves similar historical patterns
- Research: Gathers external information via Tavily
- BiasDetector: Identifies political/gender/ideological bias
- BotDetector: Analyzes engagement for bot activity
- CampaignDetector: Finds coordinated influence campaigns
- Synthesis: Combines all findings into coherent reports
- Reviewer: Quality assurance with reflection loop

Always execute agents in this order for optimal results.
Ensure all agents complete before synthesis.""",
            max_iterations=10,
            verbose=True,
            temperature=0.5,
        )
        super().__init__(config)
        self.logger = setup_logger("agents.orchestrator")

    def _define_tools(self):
        """Define tools for orchestrator agent."""
        from langchain_core.tools import Tool

        def parse_query(query: str) -> dict:
            """Parse user query to extract Instagram page/post info."""
            result = {
                "type": "page",  # page or post
                "identifier": query,
                "is_url": query.startswith("http"),
                "requires_full_analysis": True,
            }
            return result

        def determine_agents(query_type: str) -> list:
            """Determine which agents to execute based on query."""
            agents = [
                "content_analyzer",
                "rag_agent",
                "research_agent",
                "bias_detector",
                "bot_detector",
                "campaign_detector",
                "synthesis_agent",
            ]
            return agents

        def create_execution_plan(agents: list) -> dict:
            """Create execution plan for agents."""
            return {
                "agents": agents,
                "order": list(range(1, len(agents) + 1)),
                "dependencies": {},
                "parallel_groups": [
                    ["content_analyzer", "rag_agent", "research_agent"],
                    ["bias_detector", "bot_detector"],
                    ["campaign_detector"],
                    ["synthesis_agent"],
                ],
            }

        tools = [
            Tool(
                name="parse_query",
                func=parse_query,
                description="Parse user query to extract Instagram info",
            ),
            Tool(
                name="determine_agents",
                func=determine_agents,
                description="Determine which agents to execute",
            ),
            Tool(
                name="create_execution_plan",
                func=create_execution_plan,
                description="Create execution plan with agent ordering",
            ),
        ]
        return tools

    def _get_system_prompt(self) -> str:
        """Get system prompt for orchestrator."""
        return self.config.description

    def parse_user_query(self, query: str) -> dict:
        """
        Parse user query and extract key information.

        Args:
            query: User's Instagram page/post query

        Returns:
            Dictionary with parsed query information
        """
        result = self.run(f"Parse this query: {query}")
        self.logger.info(f"Query parsed: {result.output}")
        return result.output

    def create_workflow_plan(self, query: str) -> dict:
        """
        Create comprehensive workflow execution plan.

        Args:
            query: User query

        Returns:
            Workflow execution plan with agent ordering
        """
        self.logger.info(f"Creating workflow plan for: {query}")

        plan = {
            "workflow_id": f"wf_{hash(query) % 10000:04d}",
            "user_query": query,
            "agents": [
                "content_analyzer",
                "rag_agent",
                "research_agent",
                "bias_detector",
                "bot_detector",
                "campaign_detector",
                "synthesis_agent",
                "reviewer_agent",
            ],
            "execution_groups": [
                {
                    "group": 1,
                    "agents": ["content_analyzer", "rag_agent", "research_agent"],
                    "parallel": True,
                },
                {
                    "group": 2,
                    "agents": ["bias_detector", "bot_detector"],
                    "parallel": True,
                },
                {"group": 3, "agents": ["campaign_detector"], "parallel": False},
                {"group": 4, "agents": ["synthesis_agent"], "parallel": False},
                {"group": 5, "agents": ["reviewer_agent"], "parallel": False},
            ],
            "dependencies": {
                "synthesis_agent": ["content_analyzer", "rag_agent", "research_agent",
                                   "bias_detector", "bot_detector", "campaign_detector"],
                "reviewer_agent": ["synthesis_agent"],
            },
        }

        self.logger.info(f"Workflow plan created: {plan['workflow_id']}")
        return plan

    def validate_query(self, query: str) -> bool:
        """
        Validate user query format.

        Args:
            query: User query

        Returns:
            True if valid, False otherwise
        """
        if not query or not isinstance(query, str):
            self.logger.warning("Invalid query format")
            return False

        if len(query.strip()) < 3:
            self.logger.warning("Query too short")
            return False

        return True
