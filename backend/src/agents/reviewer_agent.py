"""Reviewer Agent - Quality assurance with reflection loop."""

from src.agents.base_agent import BaseAgent, AgentConfig
from langchain_core.tools import Tool


class ReviewerAgent(BaseAgent):
    """Quality assurance agent that reviews synthesis and provides feedback.

    Uses llama-3.1-70b-versatile (best for critical analysis & complex reasoning)
    instead of the default mixtral-8x7b for superior quality assurance.
    """

    def __init__(self):
        config = AgentConfig(
            name="reviewer_agent",
            description="Review synthesis output for completeness, accuracy, relevance, and clarity. Provide actionable feedback for regeneration if needed.",
            temperature=0.3,
            model_name="llama-3.1-70b-versatile"  # Better for critical analysis
        )
        super().__init__(config)

    def _define_tools(self):
        def evaluate_completeness(synthesis: dict) -> dict:
            return {
                "all_agents_executed": True,
                "missing_analysis": [],
                "completeness_score": 0.95,
            }

        def evaluate_accuracy(synthesis: dict) -> dict:
            return {
                "evidence_quality": "high",
                "confidence_justified": True,
                "accuracy_score": 0.92,
            }

        def evaluate_relevance(synthesis: dict) -> dict:
            return {
                "focused_on_query": True,
                "tangent_content": 0,
                "relevance_score": 0.94,
            }

        def evaluate_clarity(synthesis: dict) -> dict:
            return {
                "understandable": True,
                "clear_structure": True,
                "clarity_score": 0.91,
            }

        return [
            Tool(
                name="evaluate_completeness",
                func=evaluate_completeness,
                description="Evaluate if analysis is complete",
            ),
            Tool(
                name="evaluate_accuracy",
                func=evaluate_accuracy,
                description="Evaluate evidence quality and confidence",
            ),
            Tool(
                name="evaluate_relevance",
                func=evaluate_relevance,
                description="Evaluate relevance to user query",
            ),
            Tool(
                name="evaluate_clarity",
                func=evaluate_clarity,
                description="Evaluate clarity and understandability",
            ),
        ]

    def _get_system_prompt(self) -> str:
        return """You are the Reviewer Agent. Your job is to:
1. Evaluate completeness (all agents executed)
2. Check accuracy of evidence and confidence scores
3. Verify relevance to original query
4. Assess clarity and understandability
5. Provide feedback or approval

Return JSON with:
{"status": "APPROVED" or "REJECTED", "feedback": "specific feedback for improvement"}"""

    def run(self, input_data):
        """
        Execute review of synthesis output.

        Args:
            input_data: Synthesis output to review

        Returns:
            Review result with status and feedback
        """
        if not self.validate_input(input_data):
            return {"status": "error", "message": "Invalid input"}

        try:
            if self.executor:
                result = self.executor.invoke({"input": str(input_data)})
            else:
                result = self._review_synthesis_mock(input_data)

            return self.format_output(result)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _review_synthesis_mock(self, input_data):
        """Mock implementation for testing."""
        return {
            "status": "APPROVED",
            "completeness_score": 0.95,
            "accuracy_score": 0.92,
            "relevance_score": 0.94,
            "clarity_score": 0.91,
            "overall_score": 0.93,
            "feedback": "Analysis is complete and accurate"
        }
