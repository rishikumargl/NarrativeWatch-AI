"""Reflection Loop - Feedback-driven synthesis improvement."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ReflectionLoopResult:
    final_synthesis: Dict[str, Any]
    approved: bool
    iterations: int
    max_iterations: int
    feedback_history: List[Dict[str, Any]]
    status: str


class ReflectionLoop:
    """Implements feedback loop for synthesis improvement (max 3 retries)."""

    def __init__(
        self,
        synthesis_agent: Any,
        reviewer_agent: Any,
        max_retries: int = 3
    ):
        self.synthesis_agent = synthesis_agent
        self.reviewer_agent = reviewer_agent
        self.max_retries = max_retries

    def execute_with_review(
        self,
        agent_results: Dict[str, Any],
        initial_synthesis: Dict[str, Any]
    ) -> ReflectionLoopResult:
        """
        Execute synthesis with review loop (max 3 retries).

        Args:
            agent_results: Results from all detection agents
            initial_synthesis: Initial synthesis result to review

        Returns:
            ReflectionLoopResult with final synthesis and approval status
        """
        feedback_history = []
        current_synthesis = initial_synthesis
        approved = False

        for attempt in range(1, self.max_retries + 1):
            review_input = {
                "synthesis_result": current_synthesis,
                "agent_results": agent_results
            }

            review_result = self.reviewer_agent.run(review_input)

            feedback_record = {
                "iteration": attempt,
                "status": review_result["status"],
                "scores": {
                    "completeness": review_result.get("completeness_score", 0),
                    "accuracy": review_result.get("accuracy_score", 0),
                    "clarity": review_result.get("clarity_score", 0),
                    "relevance": review_result.get("relevance_score", 0)
                },
                "issues": review_result.get("issues", []),
                "suggestions": review_result.get("suggestions", [])
            }

            feedback_history.append(feedback_record)

            if review_result["status"] == "APPROVED":
                approved = True
                return ReflectionLoopResult(
                    final_synthesis=current_synthesis,
                    approved=True,
                    iterations=attempt,
                    max_iterations=self.max_retries,
                    feedback_history=feedback_history,
                    status="APPROVED"
                )

            if attempt < self.max_retries:
                feedback_prompt = self._format_feedback_for_synthesis(
                    review_result,
                    attempt,
                    self.max_retries
                )

                regen_input = {
                    "agent_results": agent_results,
                    "original_query": current_synthesis.get("original_query", ""),
                    "previous_synthesis": current_synthesis,
                    "reviewer_feedback": feedback_prompt
                }

                current_synthesis = self.synthesis_agent.run(regen_input)

        return ReflectionLoopResult(
            final_synthesis=current_synthesis,
            approved=False,
            iterations=self.max_retries,
            max_iterations=self.max_retries,
            feedback_history=feedback_history,
            status="ESCALATED"
        )

    def _format_feedback_for_synthesis(
        self,
        review_result: Dict[str, Any],
        current_attempt: int,
        max_attempts: int
    ) -> str:
        """Format reviewer feedback for synthesis regeneration."""
        lines = []

        lines.append(f"Iteration {current_attempt}/{max_attempts}: Review Feedback")
        lines.append("")

        issues = review_result.get("issues", [])
        if issues:
            lines.append("Issues to address:")
            for issue in issues:
                lines.append(f"  • {issue}")
            lines.append("")

        suggestions = review_result.get("suggestions", [])
        if suggestions:
            lines.append("Improvement suggestions:")
            for suggestion in suggestions:
                lines.append(f"  • {suggestion}")
            lines.append("")

        scores = {
            "completeness": review_result.get("completeness_score", 0),
            "accuracy": review_result.get("accuracy_score", 0),
            "clarity": review_result.get("clarity_score", 0),
            "relevance": review_result.get("relevance_score", 0)
        }

        lines.append("Current scores:")
        for key, value in scores.items():
            lines.append(f"  • {key}: {value:.1%}")
        lines.append("")

        lines.append("Please regenerate the synthesis with focus on:")
        weakest = min(scores.items(), key=lambda x: x[1])
        lines.append(f"  1. Improving {weakest[0]} (currently {weakest[1]:.1%})")
        lines.append("  2. Addressing all identified issues")
        lines.append("  3. Incorporating feedback suggestions")

        return "\n".join(lines)

    def get_loop_statistics(self, result: ReflectionLoopResult) -> Dict[str, Any]:
        """Get statistics about the reflection loop execution."""
        if not result.feedback_history:
            return {}

        avg_completeness = sum(
            f["scores"]["completeness"] for f in result.feedback_history
        ) / len(result.feedback_history)

        avg_accuracy = sum(
            f["scores"]["accuracy"] for f in result.feedback_history
        ) / len(result.feedback_history)

        avg_clarity = sum(
            f["scores"]["clarity"] for f in result.feedback_history
        ) / len(result.feedback_history)

        avg_relevance = sum(
            f["scores"]["relevance"] for f in result.feedback_history
        ) / len(result.feedback_history)

        improvement_scores = []
        for i in range(1, len(result.feedback_history)):
            prev_score = (
                result.feedback_history[i-1]["scores"]["completeness"] +
                result.feedback_history[i-1]["scores"]["accuracy"] +
                result.feedback_history[i-1]["scores"]["clarity"] +
                result.feedback_history[i-1]["scores"]["relevance"]
            ) / 4

            curr_score = (
                result.feedback_history[i]["scores"]["completeness"] +
                result.feedback_history[i]["scores"]["accuracy"] +
                result.feedback_history[i]["scores"]["clarity"] +
                result.feedback_history[i]["scores"]["relevance"]
            ) / 4

            improvement_scores.append(curr_score - prev_score)

        avg_improvement = sum(improvement_scores) / len(improvement_scores) if improvement_scores else 0

        return {
            "total_iterations": result.iterations,
            "approved": result.approved,
            "status": result.status,
            "average_completeness": avg_completeness,
            "average_accuracy": avg_accuracy,
            "average_clarity": avg_clarity,
            "average_relevance": avg_relevance,
            "average_improvement_per_iteration": avg_improvement,
            "feedback_history": result.feedback_history
        }
