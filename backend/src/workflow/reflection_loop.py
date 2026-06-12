"""Reflection Loop - Quality assurance with regeneration logic."""

from typing import Any, Optional, Callable
from src.logger import setup_logger


class ReflectionLoop:
    """
    Implements reflection loop with reviewer feedback and regeneration.

    Manages reviewer feedback, regeneration attempts, and escalation.
    """

    def __init__(self, max_retries: int = 3):
        """
        Initialize reflection loop.

        Args:
            max_retries: Maximum regeneration attempts (default 3)
        """
        self.max_retries = max_retries
        self.attempt_count = 0
        self.feedback_history = []
        self.logger = setup_logger("workflow.reflection_loop")

    def execute_with_review(
        self,
        synthesis_result: dict,
        reviewer_agent: Any,
        synthesis_agent: Any,
        original_query: str,
    ) -> dict:
        """
        Execute synthesis with review and regeneration loop.

        Args:
            synthesis_result: Initial synthesis result
            reviewer_agent: Reviewer agent instance
            synthesis_agent: Synthesis agent for regeneration
            original_query: Original user query

        Returns:
            Dictionary with final result, approval status, and attempt count
        """
        self.logger.info(f"Starting reflection loop (max {self.max_retries} attempts)")

        current_result = synthesis_result

        for attempt in range(1, self.max_retries + 1):
            self.attempt_count = attempt
            self.logger.info(f"Reflection attempt {attempt}/{self.max_retries}")

            # Get reviewer feedback
            feedback = self._get_reviewer_feedback(reviewer_agent, current_result)

            if feedback.get("status") == "APPROVED":
                self.logger.info(f"Synthesis approved on attempt {attempt}")
                return {
                    "result": current_result,
                    "approved": True,
                    "attempt": attempt,
                    "feedback_history": self.feedback_history,
                }

            # Prepare feedback for regeneration
            feedback_text = feedback.get("feedback", "Please improve the analysis")
            self.feedback_history.append(
                {
                    "attempt": attempt,
                    "feedback": feedback_text,
                    "status": feedback.get("status", "REJECTED"),
                }
            )

            # Check if we have more attempts
            if attempt < self.max_retries:
                self.logger.info(
                    f"Regenerating synthesis with feedback: {feedback_text[:100]}..."
                )

                # Regenerate with feedback
                current_result = self._regenerate_synthesis(
                    synthesis_agent, current_result, feedback_text, original_query
                )

                if current_result is None:
                    self.logger.error("Regeneration failed, using previous result")
                    current_result = current_result  # Use previous result

        # Max retries reached
        self.logger.warning(
            f"Max reflection attempts ({self.max_retries}) reached without approval"
        )
        return {
            "result": current_result,
            "approved": False,
            "attempt": self.max_retries,
            "feedback_history": self.feedback_history,
            "status": "ESCALATED",
            "escalation_reason": f"Failed to achieve approval in {self.max_retries} attempts",
        }

    def _get_reviewer_feedback(self, reviewer_agent: Any, synthesis: dict) -> dict:
        """
        Get feedback from reviewer agent.

        Args:
            reviewer_agent: Reviewer agent instance
            synthesis: Synthesis result to review

        Returns:
            Dictionary with feedback and status
        """
        try:
            result = reviewer_agent.run(str(synthesis))

            # Parse result
            if isinstance(result, dict):
                return result
            elif hasattr(result, "output"):
                return result.output if isinstance(result.output, dict) else {}
            else:
                return {"status": "REJECTED", "feedback": "Unable to parse reviewer feedback"}

        except Exception as e:
            self.logger.error(f"Reviewer agent error: {e}")
            return {
                "status": "REJECTED",
                "feedback": f"Reviewer error: {str(e)}",
            }

    def _regenerate_synthesis(
        self,
        synthesis_agent: Any,
        previous_result: dict,
        feedback: str,
        original_query: str,
    ) -> Optional[dict]:
        """
        Regenerate synthesis with feedback.

        Args:
            synthesis_agent: Synthesis agent for regeneration
            previous_result: Previous synthesis result
            feedback: Feedback from reviewer
            original_query: Original user query

        Returns:
            Regenerated synthesis result or None on failure
        """
        try:
            prompt = f"""Previous synthesis had issues. Please regenerate with improvements.

Original query: {original_query}
Feedback: {feedback}
Previous result: {str(previous_result)[:500]}...

Please improve the analysis based on the feedback."""

            result = synthesis_agent.run(prompt)

            if isinstance(result, dict):
                return result
            elif hasattr(result, "output"):
                return result.output if isinstance(result.output, dict) else None
            else:
                return None

        except Exception as e:
            self.logger.error(f"Regeneration failed: {e}")
            return None

    def get_status(self) -> dict:
        """Get current reflection loop status."""
        return {
            "attempt": self.attempt_count,
            "max_attempts": self.max_retries,
            "feedback_count": len(self.feedback_history),
            "feedback_history": self.feedback_history,
        }

    def reset(self):
        """Reset reflection loop state."""
        self.attempt_count = 0
        self.feedback_history = []
        self.logger.info("Reflection loop reset")
